import pytest

from addcorpus.python_corpora.load_corpus import load_corpus_definition
from addcorpus.models import Corpus
from es.models import Index
from indexing.models import IndexJob, CreateIndexTask
from indexing.run_job import perform_indexing

@pytest.fixture()
def mock_corpus(load_test_corpus):
    return load_test_corpus('times')


@pytest.fixture()
def corpus_definition(mock_corpus):
    corpus = load_corpus_definition(mock_corpus)
    yield corpus


@pytest.fixture()
def es_index_client(es_client, mock_corpus, test_index_cleanup):
    """
    Returns an elastic search client for the mock corpus.
    After each test, removes any indices created for the mock corpus.
    """

    yield es_client
    # delete indices when done
    indices = es_client.indices.get(index='test-times*')
    for index in indices.keys():
        es_client.indices.delete(index=index)

@pytest.fixture()
def es_alias_client(db, es_server, es_client, mock_corpus, test_index_cleanup):
    """
    Create multiple indices with version numbers for the mock corpus in elasticsearch.
    Returns an elastic search client for the mock corpus.
    """
    # add data from mock corpus
    corpus = Corpus.objects.get(name=mock_corpus)
    index = Index.objects.create(
        name='test-times-1',
        server=es_server,
    )
    job = IndexJob.objects.create(
        corpus=corpus,
    )
    CreateIndexTask.objects.create(
        job=job,
        index=index,
        delete_existing=True,
    )
    perform_indexing(job)

    es_client.indices.create(index='test-times-2')
    es_client.indices.create(index='test-times-bla-3')

    yield es_client
    # delete index when done
    indices = es_client.indices.get(index='test-times*')
    for index in indices.keys():
        es_client.indices.delete(index=index)
