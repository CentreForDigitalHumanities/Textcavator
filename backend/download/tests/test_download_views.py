import pytest
import csv
from copy import deepcopy
import io
import os

from rest_framework import status

from download.models import Download
from download import SEARCH_RESULTS_DIALECT
from addcorpus.models import Corpus
from visualization import query
from es.search import hits
from tag.models import Tag, TaggedDocument
from django.core.cache import cache


def test_direct_download_view(admin_client, mock_corpus, index_mock_corpus, csv_directory):
    request_json = {
        "corpus": mock_corpus,
        "es_query": mock_match_all_query(),
        "fields": ['date','content'],
        "size": 3,
        "route": f"/search/{mock_corpus}",
        "encoding":"utf-8"
    }
    response = admin_client.post(
        '/api/download/search_results',
        request_json,
        content_type='application/json'
    )
    assert status.is_success(response.status_code)

def test_schedule_download_view(transactional_db, admin_client, small_mock_corpus,
                                index_small_mock_corpus, celery_worker, csv_directory):
    request_json = {
        "corpus": small_mock_corpus,
        "es_query": {"query":{"bool":{"must":{"match_all":{}},"filter":[]}}},
        "fields": ['date','content'],
        "route": f"/search/{small_mock_corpus}",
        "encoding":"utf-8"
    }
    response = admin_client.post(
        '/api/download/search_results_task',
        request_json,
        content_type='application/json'
    )
    assert status.is_success(response.status_code)

def term_frequency_parameters(mock_corpus, mock_corpus_specs):
    min_year = mock_corpus_specs['min_date'].year
    max_year = mock_corpus_specs['max_date'].year
    # TODO: construct query from query module, which is much more convenient
    query_text = mock_corpus_specs['example_query']
    search_field = mock_corpus_specs['content_field']
    query = mock_es_query(query_text, search_field)
    return {
        'es_query':  query,
        'corpus_name': mock_corpus,
        'field_name': 'date',
        'bins': [
            {
                'start_date': '{}-01-01'.format(year),
                'end_date': '{}-12-31'.format(year),
                'size': 10,
            }
            for year in range(min_year, max_year + 2)
        ],
        'unit': 'year',
    }

def ngram_parameters(mock_corpus, mock_corpus_specs):
    query_text = mock_corpus_specs['example_query']
    search_field = mock_corpus_specs['content_field']
    return {
        'corpus_name': mock_corpus,
        'es_query': mock_es_query(query_text, search_field),
        'field': search_field,
        'ngram_size': 2,
        'term_position': 'any',
        'freq_compensation': 'mi',
        'subfield': 'clean',
        'max_size_per_interval': 50,
        'number_of_ngrams': 10,
        'date_field': 'date'
    }

def mock_es_query(query_text, search_field):
    q = query.MATCH_ALL
    q = query.set_query_text(q, query_text)
    q = query.set_search_fields(q, [search_field])
    return q


def mock_match_all_query():
    q = deepcopy(query.MATCH_ALL)
    q.update({'size': 3})
    return q

@pytest.mark.parametrize("visualization_type, request_parameters", [('date_term_frequency', term_frequency_parameters), ('ngram', ngram_parameters)])
def test_full_data_download_view(transactional_db, admin_client, small_mock_corpus,
                                 index_small_mock_corpus, small_mock_corpus_specs, celery_worker,
                                 csv_directory, visualization_type, request_parameters):
    parameters = request_parameters(small_mock_corpus, small_mock_corpus_specs)
    if visualization_type != 'ngram':
        # timeline and histogram expect a series of parameters
        parameters = [parameters]
    request_json = {
        'visualization': visualization_type,
        'parameters': parameters,
        'corpus_name': small_mock_corpus
    }
    response = admin_client.post(
        '/api/download/full_data',
        request_json,
        content_type='application/json'
    )
    assert status.is_success(response.status_code)

def test_empty_download_history_view(admin_client):
    response = admin_client.get(
        '/api/download/'
    )

    assert status.is_success(response.status_code)
    assert response.data == []

@pytest.fixture()
def finished_download(admin_user, csv_directory, small_mock_corpus):
    filepath = os.path.join(csv_directory, small_mock_corpus + '.csv')
    corpus = Corpus.objects.get(name=small_mock_corpus)
    download = Download.objects.create(download_type='search_results', corpus=corpus, parameters={}, user=admin_user)

    with open(filepath, 'w') as outfile:
        writer = csv.DictWriter(outfile,
            fieldnames=['content', 'date', 'genre', 'query', 'title'],
            **SEARCH_RESULTS_DIALECT)
        writer.writeheader()
        writer.writerow({
            'content': "You will rejoice to hear...",
            'date': '1818-01-01',
            'genre': 'Science fiction',
            'query': small_mock_corpus,
            'title': 'Frankenstein, or, the Modern Prometheus'
        })

    _, filename = os.path.split(filepath)
    download.complete(filename)
    return download.id

def test_download_history_view(admin_client, finished_download, small_mock_corpus):
    response = admin_client.get(
        '/api/download/'
    )

    assert status.is_success(response.status_code)
    assert len(response.data) == 1
    download = next(d for d in response.data)
    assert download['corpus'] == small_mock_corpus
    assert download['status'] == 'done'

def read_file_response(response, encoding):
    content_bytes = io.BytesIO(response.getvalue()).read()
    content_string = bytes.decode(content_bytes, encoding)
    return io.StringIO(content_string)

def test_csv_download_view(admin_client, finished_download):
    encoding = 'utf-8'
    format = 'long'
    response = admin_client.get(
        f'/api/download/csv/{finished_download}?encoding={encoding}&table_format={format}'
    )
    assert status.is_success(response.status_code)

    # read file content of response
    stream = read_file_response(response, encoding)
    reader = csv.DictReader(stream, delimiter=';')
    assert reader.fieldnames == ['content', 'date', 'genre', 'query', 'title']
    rows = [row for row in reader]
    assert len(rows) == 1

@pytest.fixture()
def some_document_id(admin_client, small_mock_corpus, index_small_mock_corpus):
    search_response = admin_client.post(
        f'/api/es/{small_mock_corpus}/_search',
        {'es_query': query.MATCH_ALL},
         content_type='application/json'
    )

    hit = hits(search_response.data)[0]
    doc_id = hit['_id']
    return doc_id

@pytest.fixture()
def tag_on_some_document(admin_client, admin_user, small_mock_corpus, some_document_id):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    tag = Tag.objects.create(
        name='fascinating',
        user=admin_user
    )
    tagged_doc = TaggedDocument.objects.create(
        corpus=corpus,
        doc_id=some_document_id
    )
    tagged_doc.tags.set([tag])
    tagged_doc.save()

    return tag


def test_download_with_tag(db, admin_client, small_mock_corpus, index_small_mock_corpus, tag_on_some_document):
    encoding = 'utf-8'
    download_request_json = {
        'corpus': small_mock_corpus,
        'es_query': mock_match_all_query(),
        'tags': [tag_on_some_document.id],
        'fields': ['date', 'content'],
        'route': f"/search/{small_mock_corpus}",
        'encoding': encoding
    }
    response = admin_client.post(
        '/api/download/search_results',
        download_request_json,
        content_type='application/json'
    )

    assert status.is_success(response.status_code)
    stream = read_file_response(response, encoding)
    reader = csv.DictReader(stream, delimiter=';')
    rows = [row for row in reader]
    assert len(rows) == 1


def test_unauthenticated_download(db, client, basic_mock_corpus, basic_corpus_public, index_basic_mock_corpus):
    download_request_json = {
        'corpus': basic_mock_corpus,
        'es_query': mock_match_all_query(),
        'fields': ['date', 'content'],
        'route': f"/search/{basic_mock_corpus}",
        'encoding': 'utf-8'
    }
    response = client.post('/api/download/search_results',
                           download_request_json,
                           content_type='application/json'
                           )
    assert status.is_success(response.status_code)
    # check that download object is removed
    download_objects = Download.objects.all()
    assert download_objects.count() == 0


def test_query_text_in_csv(db, client, basic_mock_corpus, basic_corpus_public, index_basic_mock_corpus):
    es_query = query.set_query_text(mock_match_all_query(), 'ghost')
    download_request_json = {
        'corpus': basic_mock_corpus,
        'es_query': es_query,
        'fields': ['character', 'line'],
        'route': f"/search/{basic_mock_corpus}",
        'encoding': 'utf-8'
    }
    response = client.post('/api/download/search_results',
                           download_request_json,
                           content_type='application/json'
                           )
    assert status.is_success(response.status_code)
    stream = read_file_response(response, 'utf-8')
    reader = csv.DictReader(stream, delimiter=';')
    row = next(reader)
    assert row['query'] == 'ghost'

@pytest.mark.xfail(reason='query in context download does not work')
def test_download_with_query_in_context(
    db, admin_client, small_mock_corpus, index_small_mock_corpus
):
    es_query = query.set_query_text(query.MATCH_ALL, 'the')
    es_query['highlight'] = { 'fragment_size': 200, 'fields': { 'content': {} } }
    es_query['size'] = 3
    request_json = {
        'corpus': small_mock_corpus,
        'es_query': es_query,
        'fields': ['date', 'content', 'context'],
        'route': f"/search/{small_mock_corpus}?query=the&highlight=200",
        'encoding': 'utf-8'
    }
    response = admin_client.post(
        '/api/download/search_results', request_json, content_type='application/json'
    )
    assert status.is_success(response.status_code)
