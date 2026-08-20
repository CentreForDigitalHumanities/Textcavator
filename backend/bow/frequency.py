from typing import List, Dict, Optional

from addcorpus.models import Corpus
from es.client import elasticsearch
from es.search import get_index
from bow.index_utils import bow_field_name, token_field_name
from visualization.query import MATCH_ALL, add_filter

def word_frequency(
    corpus: Corpus,
    metadata_filters: List[Dict],
    term: str,
    field: str,
    multifield: Optional[str] = None,
):
    client = elasticsearch(corpus.name)
    index = get_index(corpus.name)

    if not client.indices.exists(index=index):
        return

    query = _metadata_query(metadata_filters)
    nested_name = bow_field_name(field)
    nested_field = bow_field_name(field) + '.' + token_field_name(field, multifield)
    query['aggs'] = {
        nested_name: {
            'nested': {
                'path': nested_name
            },
            'aggs': {
                'match_tokens': {
                    'filter': {
                        'bool': {
                            'filter': [
                                {
                                    'simple_query_string': {
                                        'query': term,
                                        'fields': [nested_field]
                                    }
                                }
                            ],
                        },
                    },
                    'aggs': {
                        'token_count': {
                            'sum': { 'field': nested_name + '.:count' }
                        }
                    }
                }
            }
        }
    }
    results = client.search(
        index=index,
        size=0,
        **query,
    )
    return int(results['aggregations'][nested_name]['match_tokens']['token_count']['value'])


def most_frequent_words(
    corpus: Corpus,
    metadata_filters: List[Dict],
    field: str,
    size: int = 100,
):
    client = elasticsearch(corpus.name)
    index = get_index(corpus.name)

    if not client.indices.exists(index=index):
        return

    query = _metadata_query(metadata_filters)
    add_filter(query, { 'exists': { 'field': field }})
    nested_name = bow_field_name(field)
    query['aggs'] = {
        nested_name: {
            'nested': {
                'path': nested_name
            },
            'aggs': {
                'most_frequent': _most_frequent_aggregation(nested_name, size=size)
            }
        }
    }
    results = client.search(
        index=index,
        size=0,
        **query,
    )
    return results['aggregations'][nested_name]['most_frequent']


def _metadata_query(metadata_filters: List[Dict]):
    query = MATCH_ALL
    for f in metadata_filters:
        query = add_filter(query, f)
    return query



def _most_frequent_aggregation(nested_field, size: int = 100):
    return {
        'terms': {
            'field': nested_field + '.:token',
            'size': size,
            'order': {'token_count': 'desc'}
        },
        'aggs': {
            'token_count': {
                'sum': {'field': nested_field + '.:count'}
            }
        }
    }
