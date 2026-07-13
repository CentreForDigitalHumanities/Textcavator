import logging
import re
from django.conf import settings
from celery import shared_task, chain, group

from es import download as es_download
from download import create_csv
from download.models import Download
from addcorpus.models import Corpus
from visualization.tasks import histogram_term_frequency_tasks, timeline_term_frequency_tasks, ngram_data_tasks
from visualization import query
from download.mail import send_csv_email
from api.api_query import api_query_to_es_query

logger = logging.getLogger(__name__)

@shared_task()
def complete_download(filename, log_id):
    download = Download.objects.get(id = log_id)
    download.complete(filename)
    return log_id

@shared_task()
def complete_failed_download(request, exc, traceback, log_id):
    # request, exc, traceback are mandatory arguments for celery error handlers
    # they are already logged by celery, we only need to log the download ID
    logger.error('DOWNLOAD #{} FAILED'.format(log_id))
    try:
        download = Download.objects.get(id = log_id)
        download.complete()
    except:
        logger.error('DOWNLOAD #{} NOT FOUND IN DATABASE'.format(log_id))

@shared_task()
def download_scroll(request_json, download_size=10000):
    corpus_name = request_json['corpus']
    es_query = api_query_to_es_query(request_json, corpus_name)
    results, _ = es_download.scroll(corpus_name, es_query, download_size)
    return results


@shared_task()
def make_download(request_json, download_id, download_size=None, user=None):
    corpus_name = request_json['corpus']
    corpus = Corpus.objects.get(name=corpus_name)
    es_query = api_query_to_es_query(request_json, corpus_name)
    results, _total = es_download.scroll(
        corpus_name, es_query, download_size)

    filepath = create_csv.search_results_csv(
        results,
        request_json['fields'],
        es_query,
        download_id,
        corpus,
        user,
        request_json.get('extra', []),
    )
    return filepath


def try_download(tasks_func, download):
    '''
    Try initialising a task chain for a download. Marks the download
    as failed in the database when the chain cannot be set up.

    Parameters:
    - `task_func`: a nullary function that outputs a celery task chain
    - `download`: a Download object
    '''

    try:
        return tasks_func()
    except Exception as e:
        logger.exception('Could not create celery task')
        complete_failed_download(None, e, None, download.id)
        raise e

def download_search_results(request_json, user):
    '''
    Complete chain for downloading search results. Get results from elasticsearch
    and save as a CSV. Also saves the download action in the database.
    '''

    download_limit = user.download_limit
    corpus_name = request_json['corpus']
    corpus = Corpus.objects.get(name=corpus_name)

    download = Download.objects.create(download_type='search_results', corpus=corpus, parameters=request_json, user=user)

    make_chain = lambda: chain(
        make_download.s(request_json, download.id, download_limit, user),
        complete_download.s(download.id),
        csv_data_email.s(user.email, user.get_short_name()),
    ).on_error(complete_failed_download.s(download.id))

    return try_download(make_chain, download)

@shared_task()
def make_full_data_csv(results_per_series, visualization_type, parameters_per_series, log_id):
    '''
    Export term frequency results to a csv.
    '''
    if visualization_type == 'ngram':
        return create_csv.ngram_csv(results_per_series, log_id)
    query_per_series, field_name, unit = extract_term_frequency_download_metadata(parameters_per_series)
    return create_csv.term_frequency_csv(query_per_series, results_per_series, field_name, log_id, unit = unit)


def term_frequency_full_data_tasks(parameters_per_series, visualization_type):
    '''
    Returns a group of tasks which retrieve results for the full data of a
    term frequency graph.
    '''

    parameters_unlimited = map(remove_size_limit, parameters_per_series)
    task_function = histogram_term_frequency_tasks if visualization_type == 'aggregate_term_frequency' else timeline_term_frequency_tasks
    return group(
        task_function(series_parameters, True) for series_parameters in parameters_unlimited
    )

def ngram_full_data_tasks(ngram_parameters, dummy):
    ngram_parameters['max_size_per_interval'] = None
    return ngram_data_tasks(ngram_parameters)

def extract_term_frequency_download_metadata(parameters_per_series):
    '''
    Get some relevant metadata for a term frequency request:
    - The query text for each series
    - The name of the x-axis field
    - The unit on the x-axis, in case of date fields
    '''

    query_per_series = [query.get_query_text(params['es_query']) for params in parameters_per_series]
    field_name = parameters_per_series[0]['field_name']
    unit = parameters_per_series[0].get('unit')
    return query_per_series, field_name, unit

def remove_size_limit(parameters):
    '''
    Removes the size (document limit) specification from term frequency
    parameters. The new parameters can be used to get term frequencies
    without a document limit.
    '''

    for bin in parameters['bins']:
        bin['size'] = None
    return parameters

@shared_task()
def csv_data_email(log_id, user_email, name):
    '''
    Send an email to the user that their CSV is ready
    '''

    logger.info('should now be sending email')

    send_csv_email(user_email, name, log_id)

def download_full_data(request_json, user):
    '''
    Download the full data for a visualisation
    '''
    visualization_type = request_json['visualization']

    task_per_type = {
        'date_term_frequency': term_frequency_full_data_tasks,
        'aggregate_term_frequency': term_frequency_full_data_tasks,
        'ngram': ngram_full_data_tasks,
    }

    parameters = request_json['parameters']
    corpus_name = request_json['corpus_name']
    corpus = Corpus.objects.get(name=corpus_name)
    task = task_per_type[visualization_type](parameters, visualization_type)

    download = Download.objects.create(
        download_type=visualization_type, corpus=corpus, parameters=parameters, user=user)

    make_chain = lambda : chain(
        task,
        make_full_data_csv.s(visualization_type, parameters, download.id),
        complete_download.s(download.id),
        csv_data_email.s(user.email, user.get_short_name()),
    ).on_error(complete_failed_download.s(download.id))

    return try_download(make_chain, download)
