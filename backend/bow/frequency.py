from typing import List, Dict, Optional

from addcorpus.models import Corpus
from es.client import elasticsearch
from es.search import get_index
from bow.index_utils import bow_index_name, content_field_name
from visualization.query import MATCH_ALL, add_filter, set_query_text, set_search_fields

def word_frequency(
    corpus: Corpus,
    metadata_filters: List[Dict],
    term: str,
    field: str,
    multifield: Optional[str] = None,
):
    client = elasticsearch(corpus.name)
    index = bow_index_name(get_index(corpus.name))

    if not client.indices.exists(index=index):
        return

    query = _word_query(metadata_filters, term, field, multifield)
    query['aggs'] = {
        'token_count': {
            'sum': { 'field': ':count' }
        }
    }
    results = client.search(
        index=index,
        size=0,
        **query,
    )
    return int(results['aggregations']['token_count']['value'])


def most_frequent_words(
    corpus: Corpus,
    metadata_filters: List[Dict],
    field: str,
    size: int = 100,
):
    client = elasticsearch(corpus.name)
    index = bow_index_name(get_index(corpus.name))

    if not client.indices.exists(index=index):
        return

    query = _metadata_query(metadata_filters)
    add_filter(query, { 'exists': { 'field': field }})
    query['aggs'] = {'most_frequent': _most_frequent_aggregation(size=size)}
    results = client.search(
        index=index,
        size=0,
        **query,
    )
    return results['aggregations']['most_frequent']


def _metadata_query(metadata_filters: List[Dict]):
    query = MATCH_ALL
    for f in metadata_filters:
        query = add_filter(query, f)
    return query


def _word_query(
    metadata_filters: List[Dict],
    term: str,
    field: str,
    multifield: Optional[str] = None,
):
    query = _metadata_query(metadata_filters)
    field_name = content_field_name(field, multifield)
    query = set_query_text(query, term)
    query = set_search_fields(query, [field_name])
    return query


def _most_frequent_aggregation(size: int = 100):
    return {
        'terms': {
            'field': ':token',
            'size': size,
            'order': {'token_count': 'desc'}
        },
        'aggs': {
            'token_count': {
                'sum': {'field': ':count'}
            }
        }
    }
