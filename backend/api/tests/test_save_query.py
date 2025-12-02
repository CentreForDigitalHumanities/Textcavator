from django.utils import timezone
import pytest
from copy import deepcopy

from visualization.query import MATCH_ALL, set_query_text
from addcorpus.models import Corpus
from api.models import Query
from api.save_query import recent_queries, same_query


@pytest.fixture()
def saved_query(auth_user, db, small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    return Query.objects.create(
        query_json={'es_query': MATCH_ALL},
        user=auth_user,
        corpus=corpus,
        completed=timezone.now(),
        transferred=10,
        total_results=10,
    )


def test_recent_queries(auth_user, saved_query):
    assert saved_query in recent_queries(auth_user)

    saved_query.started = timezone.datetime(2000, 1, 1, 0, 0, tzinfo=timezone.get_current_timezone())
    saved_query.completed = timezone.datetime(2000, 1, 1, 0, 0, tzinfo=timezone.get_current_timezone())
    saved_query.save()

    assert saved_query not in recent_queries(auth_user)

def test_same_query():
    q = {
        'es_query': MATCH_ALL
    }

    assert same_query(q, q)

    q1 = deepcopy(q)
    q1['es_query'].update({
        'size': 20,
        'from': 21,
    })

    assert same_query(q1, q)

    q2 = deepcopy(q)
    q2['es_query'] = set_query_text(q2['es_query'], 'test')
    assert not same_query(q2, q)

    q3 = deepcopy(q)
    q3.update({
        'tags': [1]
    })

    assert not same_query(q3, q)
