from typing import Iterable, Tuple, Dict, Any
from elasticsearch import Elasticsearch

from addcorpus.models import Corpus
from es.client import elasticsearch
from es.search import hits
from visualization.query import MATCH_ALL
from visualization.termvectors import request_termvectors_batched, get_terms
from bow.index_utils import bow_field_name




def iterate_documents(client: Elasticsearch, index: str, query: Dict):
    '''
    Iterate through documents in an index.
    Unlike download.scroll, this is not affected by scroll timeouts.
    '''
    body = query | { 'index': index, 'allow_no_indices': False, 'sort': ['_doc'], 'size': 1000, }
    result = client.search(**body)
    docs = hits(result)
    while len(docs):
        yield from docs
        last = docs[-1]
        body = body | { 'search_after': last['sort'] }
        result = client.search(**body)
        docs = hits(result)


def collect_tokens(
    corpus: Corpus, index_name: str, field_name: str, threshold=0,
) -> Iterable[Tuple[str, Dict[str, int], Dict[str, Any], str]]:
    client = elasticsearch(corpus)
    docs = iterate_documents(client, index_name, MATCH_ALL)
    for hit, vectors in request_termvectors_batched(docs, client, True, [field_name]):
        terms = get_terms(vectors, field_name)
        if terms:
            counts = {
                term: {
                    ':count': data['term_freq'],
                    ':total_count': data['ttf'],
                }
                for term, data in terms.items()
                if data['ttf'] >= threshold
            }
            yield hit['_id'], counts


def token_data(corpus: Corpus, index_name: str, field_name: str,  threshold=0):
    iterator = collect_tokens(corpus, index_name, field_name, threshold=threshold)
    for doc_id, term_counts in iterator:
        data = {bow_field_name(field_name): [
                {':token': term, field_name: term} | term_count_data
                for term, term_count_data in term_counts.items()
            ]
        }
        yield doc_id, data
