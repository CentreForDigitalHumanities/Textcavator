import pytest

from api.models import Query
from es.search import hits
from visualization.query import MATCH_ALL

FORWARD_CASES = {
    # search corpus to which the user has no access (rejected)
    'search_restricted_corpus': (
        False,
        '/api/es/small-mock-corpus/_search?size=20&scroll=3m',
        { 'es_query': {'query': {'bool': {
            'must': {'simple_query_string': {
                'query': 'universally',
                'lenient': True,
                'default_operator': 'or',
            }},
            'filter': [],
        }}}},
        None,
        401,
    ),
    # valid search with no matching results (passes but empty results)
    'search_bogus': (
        True,
        '/api/es/small-mock-corpus/_search?size=20&scroll=3m',
        { 'es_query': {'query': {'bool': {
            'must': {'simple_query_string': {
                'query': 'pineapple',
                'lenient': True,
                'default_operator': 'or',
            }},
            'filter': [],
        }}}},
        0,
        200,
    ),
    # corpus does not exist (rejected)
    'search_nonexistent': (
        True,
        '/api/es/nonexistent-corpus/_search?size=20&scroll=3m',
        { 'es_query': {'query': {'bool': {
            'must': {'simple_query_string': {
                'query': 'universally',
                'lenient': True,
                'default_operator': 'or',
            }},
            'filter': [],
        }}}},
        None,
        404,
    ),
    # same corpus name specified in both path and request body (passes normally)
    'search_double_corpus_name': (
        True,
        '/api/es/small-mock-corpus/_search?size=20&scroll=3m',
        {
            'es_query': {'query': {'bool': {
                'must': {'simple_query_string': {
                    'query': 'universally',
                    'lenient': True,
                    'default_operator': 'or',
                }},
                'filter': [],
            }}},
            'corpus': 'small-mock-corpus'
        },
        1,
        200,
    ),
    # conflicting corpus names in path vs. body (rejected)
    'search_conflicting_corpus_name': (
        True,
        '/api/es/small-mock-corpus/_search?size=20&scroll=3m',
        {
            'es_query': {'query': {'bool': {
                'must': {'simple_query_string': {
                    'query': 'universally',
                    'lenient': True,
                    'default_operator': 'or',
                }},
                'filter': [],
            }}},
            'corpus': 'basic-mock-corpus'
        },
        None,
        400,
    ),
    # request missing body (rejected)
    'search_empty': (
        True,
        '/api/es/small-mock-corpus/_search?size=20&scroll=3m',
        {},
        3,
        200,
    ),
    # normal search
    'search_success': (
        True,
        '/api/es/small-mock-corpus/_search?size=20&scroll=3m',
        {'es_query': {'query': {'bool': {
            'must': {'simple_query_string': {
                'query': 'universally',
                'lenient': True,
                'default_operator': 'or',
            }},
            'filter': [],
        }}}},
        1,
        200,
    ),
}

@pytest.fixture(params=FORWARD_CASES.values(), ids=list(FORWARD_CASES.keys()))
def scenario(request):
    return request.param

def test_es_forwarding_views(scenario, index_small_mock_corpus, client, small_mock_corpus_user):
    (authenticate, route, data,
     n_hits, status) = scenario

    if authenticate:
        client.force_login(small_mock_corpus_user)

    response = client.post(route, data, content_type = 'application/json')
    assert response.status_code == status

    if response.status_code == 200:
        assert len(hits(response.data)) == n_hits

def test_search_history_is_saved(small_mock_corpus, small_mock_corpus_user, index_small_mock_corpus, client):
    assert small_mock_corpus_user.queries.count() == 0

    client.force_login(small_mock_corpus_user)

    search = lambda: client.post(
        f'/api/es/{small_mock_corpus}/_search',
        {'es_query': MATCH_ALL},
        content_type='application/json',
    )

    response = search()

    assert response.status_code == 200
    assert small_mock_corpus_user.queries.count() == 1

    response2 = search()

    assert response2.status_code == 200
    assert small_mock_corpus_user.queries.count() == 1


def test_unauthenticated_search(client, basic_mock_corpus, basic_corpus_public, index_basic_mock_corpus):
    queries_before_search = Query.objects.count()
    response = client.post(
        f'/api/es/{basic_mock_corpus}/_search',
        {'es_query': MATCH_ALL},
        content_type='application/json',
    )
    assert response.status_code == 200
    assert Query.objects.count() == queries_before_search
