from time import sleep
from addcorpus.models import Corpus
from analysis.create_index_job import create_token_index_job
from es.client import elasticsearch
from indexing.run_job import perform_indexing
from visualization.query import MATCH_ALL
from es.search import total_hits

def test_token_indexing(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    job = create_token_index_job(corpus)
    perform_indexing(job)

    client = elasticsearch(small_mock_corpus)
    index = 'test-small-mock-corpus.tokens'
    assert client.indices.exists(index=index)
    sleep(1)
    results = client.search(
        index=index,
        **MATCH_ALL,
    )
    assert total_hits(results) > 0
