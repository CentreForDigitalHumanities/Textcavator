import pytest
from datetime import datetime
from time import sleep

from addcorpus.models import Corpus
from indexing.models import TaskStatus
from indexing.run_job import perform_indexing
from indexing.create_job import create_indexing_job

START = datetime.strptime('1970-01-01', '%Y-%m-%d')
END = datetime.strptime('1970-12-31', '%Y-%m-%d')


@pytest.mark.parametrize("prod, name, shards", [(True, "test-times-1", '5'), (False, "test-times", '1')])
def test_prod_flag(mock_corpus, es_index_client, corpus_definition, prod, name, shards):
    corpus = Corpus.objects.get(name=mock_corpus)
    job = create_indexing_job(
        corpus, START, END,
        mappings_only=True, add=False, clear=False, prod=prod, rollover=False,
    )
    perform_indexing(job)

    assert es_index_client.indices.exists(index=name)
    assert es_index_client.indices.get_settings(index=name).get(
        name)['settings']['index']['number_of_shards'] == shards


@pytest.mark.parametrize("mappings_only, expected", [(False, 2), (True, 0)])
def test_mappings_only_flag(mock_corpus, es_index_client, corpus_definition, mappings_only, expected):
    corpus = Corpus.objects.get(name=mock_corpus)
    job = create_indexing_job(
        corpus, START, END,
        mappings_only=mappings_only, add=False, clear=False, prod=False, rollover=False,
    )
    perform_indexing(job)
    sleep(1)
    res = es_index_client.count(index='test-times*')
    assert res.get('count') == expected


def test_add_clear(db, mock_corpus, es_index_client):
    corpus = Corpus.objects.get(name=mock_corpus)
    job = create_indexing_job(
        corpus, START, END,
        mappings_only=True, add=False, clear=False, prod=False, rollover=False,
    )
    perform_indexing(job)
    res = es_index_client.count(index='test-times*')
    assert res.get('count') == 0
    job = create_indexing_job(
        corpus, START, END,
        mappings_only=False, add=True, clear=False, prod=False, rollover=False,
    )
    perform_indexing(job)
    sleep(1)
    res = es_index_client.count(index='test-times*')
    assert res.get('count') == 2
    job = create_indexing_job(
        corpus, START, END,
        mappings_only=True, add=False, clear=True, prod=False, rollover=False,
    )
    perform_indexing(job)
    res = es_index_client.count(index='test-times*')
    assert res.get('count') == 0


def test_mismatch_corpus_index_names(mock_corpus, corpus_definition, es_index_client):
    assert corpus_definition.es_index != mock_corpus


def test_db_only_corpus(json_mock_corpus, es_client, index_json_mock_corpus):
    res = es_client.count(index=json_mock_corpus.configuration.es_index)
    assert res.get('count') == 10


def test_indexing_with_version(mock_corpus, corpus_definition, es_index_client):
    corpus = Corpus.objects.get(name=mock_corpus)
    job = create_indexing_job(
        corpus,
        START,
        END,
        mappings_only=False,
        add=False,
        clear=False,
        prod=True,
        rollover=True,
    )
    perform_indexing(job)
    assert es_index_client.indices.exists(index="test-times-1") == True


def test_task_status_success(mock_corpus, es_index_client):
    '''Test task status on a successful job'''
    corpus = Corpus.objects.get(name=mock_corpus)
    job = create_indexing_job(corpus, START, END)
    create_task = job.createindextasks.first()
    assert create_task.status == TaskStatus.CREATED

    perform_indexing(job)

    create_task.refresh_from_db()
    assert create_task.status == TaskStatus.DONE

def test_task_status_failure(mock_corpus, es_index_client):
    '''Test task status is stored properly when the job fails'''
    corpus = Corpus.objects.get(name=mock_corpus)

    # create index for this corpus
    job = create_indexing_job(corpus, START, END, mappings_only=True)
    perform_indexing(job)

    # create a second job to create the same index ; will fail because the index
    # already exists
    invalid_job = create_indexing_job(corpus, START, END)

    with pytest.raises(Exception):
        perform_indexing(invalid_job)

    create_task = invalid_job.createindextasks.first()
    assert create_task.status == TaskStatus.ERROR
    populate_task = invalid_job.populateindextasks.first()
    assert populate_task.status == TaskStatus.CANCELLED


def test_task_status_invalid(json_mock_corpus, es_index_client):
    '''Test task status is set property when validation on the corpus fails'''

    corpus = json_mock_corpus
    corpus.configuration.fields.all().delete()
    assert not corpus.ready_to_index()

    job = create_indexing_job(corpus, START, END)
    perform_indexing(job)

    assert job.status() == TaskStatus.CANCELLED
