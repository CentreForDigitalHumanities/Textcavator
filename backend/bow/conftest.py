from time import sleep
import pytest
from addcorpus.models import Corpus
from bow.create_index_job import create_bow_index_job
from indexing.run_job import perform_indexing
from indexing.create_job import create_indexing_job


@pytest.fixture()
def index_small_mock_corpus_bow(small_mock_corpus, es_client, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    job = create_bow_index_job(corpus)
    perform_indexing(job)
    sleep(1)

    yield

    # reset index
    reset = create_indexing_job(corpus, clear=True)
    perform_indexing(reset)
    sleep(1)
