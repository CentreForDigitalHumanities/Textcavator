from typing import Dict
from es.client import elasticsearch, server_for_corpus
from addcorpus.models import Corpus
from django.conf import settings

def get_index(corpus_name: str) -> str:
    corpus = Corpus.objects.get(name=corpus_name)
    if corpus.configuration.es_index:
        return corpus.configuration.es_index

    config = settings.SERVERS.get(server_for_corpus(corpus.name))
    prefix = config.get('index_prefix', None)
    name = corpus.name if corpus.has_python_definition else f'custom[{corpus.pk}]'
    return f'{prefix}-{name}' if prefix else name

def search(corpus_name: str, query_model: Dict = {}, client = None, **kwargs):
    """
    Make a basic search request.

    Parameters:
    - `corpus`: name of the Corpus object
    - `query_model`: a query dict (optional)
    - `client`: an elasticsearch client (optional). Provide this if there is already
    and active client in the session. If left out, a new client will be instantiated.
    - kwargs: any arguments that should be passed on to the `search()` function of
    the elasticsearch client
    """
    index = get_index(corpus_name)

    if not client:
        client = elasticsearch(corpus_name)

    search_result = client.search(
        index=index,
        **query_model,
        **kwargs,
    )
    return search_result

def total_hits(search_result):
    return search_result['hits']['total']['value']

def hits(search_result):
    return search_result['hits']['hits']

def aggregation_results(search_result):
    return search_result['aggregations']
