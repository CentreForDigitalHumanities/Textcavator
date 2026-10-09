import logging
from elasticsearch import Elasticsearch

from es.search import hits
from es.sync import update_availability
from indexing.models import ReindexTask
from indexing.run_populate_task import run_bulk

logger = logging.getLogger('indexing')


def iterate_documents(client: Elasticsearch, index: str):
    '''
    Iterate through documents in an index.
    Unlike download.scroll, this is not affected by scroll timeouts.
    '''
    body = {
        'index': index,
        'query': { 'match_all': {}},
        'allow_no_indices': False,
        'sort': ['_doc'],
        'size': 1000,
    }
    result = client.search(**body)
    docs = hits(result)
    while len(docs):
        yield from docs
        last = docs[-1]
        body = body | { 'search_after': last['sort'] }
        result = client.search(**body)
        docs = hits(result)


def run_reindex_task(task: ReindexTask):
    '''
    Reindex documents from one index to another.

    This uses a query to fetch documents and then sends bulk index requests to
    Elasticsearch (similar to the the populate action). This adds some overhead
    compared to the reindex API from ES, but it works reliably and can transfer
    data between unconnected clusters.
    '''
    update_availability(task.source_index)
    if not task.source_index.available:
        raise Exception(f'source index {task.source_index} is not available')

    docs = iterate_documents(task.source_index.client(), task.source_index.name)
    actions = (
        {
            '_op_type': 'index',
            '_index': task.index.name,
            '_id': doc.get('_id'),
            '_source': doc.get('_source'),
        }
        for doc in docs
    )
    run_bulk(task, actions)
