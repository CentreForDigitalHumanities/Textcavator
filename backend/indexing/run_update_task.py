from typing import TYPE_CHECKING
import logging
from django.conf import settings

from addcorpus.python_corpora.corpus import CorpusDefinition
from es.client import elasticsearch
from addcorpus.python_corpora.load_corpus import load_corpus_definition
from addcorpus.exceptions import PythonDefinitionRequired
if TYPE_CHECKING:
    from indexing.models import UpdateIndexTask

logger = logging.getLogger('indexing')

def run_update_task(task: 'UpdateIndexTask') -> None:
    if not task.corpus.has_python_definition:
        raise PythonDefinitionRequired(task.corpus, 'Update task not applicable')

    corpus_definition = load_corpus_definition(task.corpus.name)

    if corpus_definition.update_body():
        min_date = task.document_min_date or task.corpus.configuration.min_date
        max_date = task.document_max_date or task.corpus.configuration.min_date
        update_index(
            task.corpus.name,
            corpus_definition,
            corpus_definition.update_query(
                min_date=min_date.strftime('%Y-%m-%d'),
                max_date=max_date.strftime('%Y-%m-%d')
        ))
    elif corpus_definition.update_script():
        update_by_query(
            task.corpus.name, corpus_definition, corpus_definition.update_script()
        )
    else:
        raise RuntimeError("Cannot update without update_body or update_script")


def update_index(corpus: str, corpus_definition: CorpusDefinition, query_model):
    ''' update information for fields in the index
    requires the definition of the functions
    - update_query
    (restricts which documents are updated)
    - update_body
    (defines which fields should be updated with which value)
    in the corpus definition class
    '''
    client = elasticsearch(corpus)
    scroll_timeout, scroll_size = get_es_settings(corpus, corpus_definition)
    results = client.search(
        index=corpus,
        size=scroll_size,
        scroll=scroll_timeout,
        body=query_model,
        timeout=settings.ES_SEARCH_TIMEOUT
    )
    hits = len(results['hits']['hits'])
    total_hits = results['hits']['total']
    for doc in results['hits']['hits']:
        update_body = corpus_definition.update_body(doc)
        update_document(corpus, doc, update_body, client)
    while hits<total_hits:
        scroll_id = results['_scroll_id']
        for doc in results['hits']['hits']:
            update_body = corpus_definition.update_body(doc)
            update_document(corpus, doc, update_body, client)
        results = client.scroll(scroll_id=scroll_id,
            scroll=scroll_timeout)
        hits += len(results['hits']['hits'])
        logger.info("Updated {} of {} documents".format(hits, total_hits))


def update_by_query(corpus: str, corpus_definition: CorpusDefinition, query_generator):
    client = elasticsearch(corpus)
    scroll_timeout, scroll_size = get_es_settings(corpus, corpus_definition)
    for query_model in query_generator:
        response = client.update_by_query(
            index=corpus,
            size=scroll_size,
            scroll=scroll_timeout,
            body=query_model,
            timeout=settings.ES_SEARCH_TIMEOUT
        )
        if response['updated']==0:
            logger.info('No documents updated for query {}'.format(query_model))


def update_document(corpus: str, doc, update_body, client=None):
    if not client:
        client = elasticsearch(corpus)
    doc_id = doc.get('_id', doc.get('id', None))
    if not doc_id:
        logger.info("failed to update the following document: {}".format(doc))
        return None
    client.update(index=corpus, id=doc_id, body=update_body)



def get_es_settings(corpus: str, corpus_definition):
    """ Get the settings for the scroll request.
    Return:
    - scroll_timeout
    - scroll_size
    """
    server = settings.CORPUS_SERVER_NAMES.get(corpus, 'default')
    scroll_timeout = settings.SERVERS[server]['scroll_timeout']
    scroll_size = settings.SERVERS[server]['scroll_page_size']
    return scroll_timeout, scroll_size
