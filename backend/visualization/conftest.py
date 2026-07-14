import pytest
import os
import random

from corpora_test.small.small_mock_corpus import SPECS as SMALL_MOCK_CORPUS_SPECS
from corpora_test.large.large_mock_corpus import SPECS as LARGE_MOCK_CORPUS_SPECS

here = os.path.abspath(os.path.dirname(__file__))

class MockClient(object):
    '''Mock ES Client returning fixed number of (empty) hits'''
    def __init__(self, num_hits):
        self.num_hits = num_hits

    def search(self, index, size, **kwargs):
        return {'hits':
            {'total': {'value': self.num_hits},
            'hits': [{'_id': hit_id, '_index': index} for hit_id in range(min(size, self.num_hits))]},
            '_scroll_id': '42'
        }

    def clear_scroll(self, scroll_id):
        return {'status': 'ok'}


@pytest.fixture(params=['small-mock-corpus', 'large-mock-corpus'])
def mock_corpus(request):
    'parametrised version of the mock corpus fixtures: runs with both'

    return request.param

@pytest.fixture()
def small_mock_corpus_specs():
    '''Return various specifications for the mock corpus (number of documents etc.)'''
    return SMALL_MOCK_CORPUS_SPECS

@pytest.fixture()
def large_mock_corpus_specs():
    '''Return various specifications for the mock corpus (number of documents etc.)'''
    return LARGE_MOCK_CORPUS_SPECS

@pytest.fixture()
def mock_corpus_specs(mock_corpus, small_mock_corpus, large_mock_corpus,
                      small_mock_corpus_specs, large_mock_corpus_specs):
    '''Return various specifications for the mock corpus (number of documents etc.)'''

    specs = {
        small_mock_corpus: small_mock_corpus_specs,
        large_mock_corpus: large_mock_corpus_specs,
    }
    return specs[mock_corpus]


@pytest.fixture()
def index_mock_corpus(mock_corpus, index_small_mock_corpus, index_large_mock_corpus):
    '''Create and populate an index for the mock corpus.'''

    yield mock_corpus

@pytest.fixture
def basic_query():
    return {
        "query": {
            "bool": {
                "must": {
                    "simple_query_string": {
                        "query": "test",
                        "lenient": True,
                        "default_operator": "or"
                    }
                },
                "filter": []
            }
        }
    }

