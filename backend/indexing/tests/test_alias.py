import pytest

from addcorpus.models import Corpus
from indexing.create_job import create_alias_job
from indexing.run_job import perform_indexing


def test_alias(db, es_alias_client):
    corpus = Corpus.objects.get(name='times')
    assert corpus.configuration.es_index == 'test-times'
    job = create_alias_job(corpus)
    perform_indexing(job)
    res = es_alias_client.indices.get_alias(name=corpus.configuration.es_index)
    assert res.get('test-times-2') is not None


def test_alias_with_clean(es_alias_client):
    corpus = Corpus.objects.get(name='times')
    indices = es_alias_client.indices.get(
        index='{}-*'.format(corpus.configuration.es_index))
    assert 'test-times-1' in list(indices.keys())
    job = create_alias_job(corpus, True)
    perform_indexing(job)
    indices = es_alias_client.indices.get(
        index='{}-*'.format(corpus.configuration.es_index))
    assert 'test-times-1' not in list(indices.keys())

def test_alias_with_unversioned_index(es_alias_client):
    '''
    Tests that alias command fails if there is already an unversioned index.
    '''
    es_alias_client.indices.delete(index='test-times-1,test-times-2')
    es_alias_client.indices.create(index='test-times')

    corpus = Corpus.objects.get(name='times')
    with pytest.raises(Exception):
        create_alias_job(corpus)


def test_extra_alias(db, es_alias_client):
    '''
    Tests alias command when a corpus uses `es_alias` to create a shared alias with
    other corpora.
    '''

    corpus = Corpus.objects.get(name='times')

    assert es_alias_client.indices.put_alias(index='test-times-1', name='test-times')
    assert es_alias_client.indices.put_alias(index='test-times-1', name='test-newspapers')
    es_alias_client.indices.create(index='test-guardian-1')
    es_alias_client.indices.put_alias(index='test-guardian-1', name='test-newspapers')

    corpus.configuration.es_alias = 'test-newspapers'
    corpus.configuration.save()

    job = create_alias_job(corpus)
    perform_indexing(job)

    # test-times-2 has own name and additional alias
    assert es_alias_client.indices.get_alias(name='test-times').get('test-times-2')
    assert es_alias_client.indices.get_alias(name='test-newspapers').get('test-times-2')

    # alias is rolled over from test-times-1
    assert not es_alias_client.indices.get_alias(name='test-times').get('test-times-1')
    assert not es_alias_client.indices.get_alias(name='test-newspapers').get('test-times-1')

    # shared alias on test-guardian-1 is kept
    assert es_alias_client.indices.get_alias(name='test-newspapers').get('test-guardian-1')
