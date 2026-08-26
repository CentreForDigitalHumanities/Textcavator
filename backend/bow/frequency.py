from typing import Dict, Optional

from addcorpus.models import Corpus
from es.client import elasticsearch
from es.search import get_index
from bow.index_utils import bow_field_name, token_field_name, has_bow_field
from visualization.query import add_filter

def word_frequency(
    corpus: Corpus,
    query: Dict,
    term: str,
    field: str,
    multifield: Optional[str] = None,
):
    client = elasticsearch(corpus.name)
    index = get_index(corpus.name)

    if not has_bow_field(client, index, field):
        return None

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
    query['size'] = 0
    results = client.search(
        index=index,
        **query,
    )
    return int(results['aggregations'][nested_name]['match_tokens']['token_count']['value'])


def most_frequent_words(
    corpus: Corpus,
    query: Dict,
    field: str,
    size: int = 100,
):
    client = elasticsearch(corpus.name)
    index = get_index(corpus.name)

    if not has_bow_field(client, index, field):
        return None

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
    query['size'] = 0
    results = client.search(
        index=index,
        **query,
    )
    return results['aggregations'][nested_name]['most_frequent']


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
