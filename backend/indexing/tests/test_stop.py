from time import sleep
from elasticsearch import Elasticsearch
from es import search
from visualization.query import MATCH_ALL

from addcorpus.models import Corpus
from indexing import models, create_job, run_job, stop_job, constants

def mock_documents(size):
    for _ in range(size):
        yield {}

def test_stop_job(transactional_db, mock_corpus, es_index_client: Elasticsearch, celery_worker, monkeypatch):
    # replace populate task handler to ensure fixed execution time
    def mock_populate(task: models.PopulateIndexTask):
        for doc in mock_documents(20):
            stop_job.raise_if_aborted(task)
            es_index_client.index(
                index='test-times',
                document=doc,
            )
            sleep(1)
        return task.index.name

    monkeypatch.setattr(models.PopulateIndexTask, 'handle', mock_populate)

    # start indexing job asynchronously
    corpus = Corpus.objects.get(name=mock_corpus)
    job =  create_job.create_indexing_job(corpus)
    result = run_job.perform_indexing_async(job)

    # wait for start_job task to complete
    first_result = result.parent.parent
    first_result.get()
    # let job run for a while
    sleep(2)

    # stop
    assert stop_job.is_stoppable(job)
    stop_job.mark_tasks_stopped(job)

    result.get() # complete execution
    sleep(1) # make sure ES is done processing

    assert job.status() == constants.TaskStatus.ABORTED
    result = search.search(mock_corpus, MATCH_ALL, es_index_client)
    assert 0 < search.total_hits(result) < 20

