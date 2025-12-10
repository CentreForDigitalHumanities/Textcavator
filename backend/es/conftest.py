import pytest
from django.contrib.auth.models import Group

from addcorpus.python_corpora.load_corpus import load_corpus_definition
from addcorpus.models import Corpus


@pytest.fixture(scope='session')
def mock_corpus():
    return 'times'


@pytest.fixture()
def corpus_definition(mock_corpus):
    corpus = load_corpus_definition(mock_corpus)
    yield corpus


@pytest.fixture()
def small_mock_corpus_user(auth_user, small_mock_corpus):
    group = Group.objects.create(name='corpus access')
    corpus = Corpus.objects.get(name=small_mock_corpus)
    corpus.groups.add(group)
    corpus.save()
    auth_user.groups.add(group)
    auth_user.save()
    return auth_user
