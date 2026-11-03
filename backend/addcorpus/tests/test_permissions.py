import pytest
from addcorpus.permissions import corpus_name_from_request

cases = [
    (
        {'kwargs': {'corpus': 'my-corpus'}, 'query': {}, 'data': {}},
        'my-corpus',
        True,
    ),
    (
        {'kwargs': {'corpus': 'also-my-corpus'}, 'query': {}, 'data': {}},
        'also-my-corpus',
        True,
    ),
    (
        {'kwargs': {}, 'query': {'corpus': 'my-corpus'}, 'data': {}},
        'my-corpus',
        True,
    ),
    (
        {'kwargs': {}, 'query': {'corpus_name': 'my-corpus'}, 'data': {}},
        'my-corpus',
        True,
    ),
    (
        {'kwargs': {}, 'query': {}, 'data': {'corpus': 'my-corpus'}},
        'my-corpus',
        True,
    ),
    (
        {'kwargs': {'corpus': 'my-corpus'}, 'query': {}, 'data': {'corpus': 'my-corpus'}},
        'my-corpus',
        True,
    ),
    (
        {'kwargs': {'corpus': 'my-corpus'}, 'query': {}, 'data': {'corpus': 'not-my-corpus'}},
        None,
        False,
    ),
]


class MockRequest:
    def __init__(self, kwargs, query_params, data):
        self.parser_context = {
            'kwargs': kwargs
        }
        self.query_params = query_params
        self.data = data


def test_corpus_name_from_request():
    for data, name, success in cases:
        request = MockRequest(data['kwargs'], data['query'], data['data'])
        if success:
            assert corpus_name_from_request(request) == name
        else:
            with pytest.raises(Exception):
                corpus_name_from_request(request)
