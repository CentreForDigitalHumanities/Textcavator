from time import sleep
from addcorpus.models import Corpus
from analysis.create_index_job import create_token_index_job
from es.client import elasticsearch
from indexing.run_job import perform_indexing
from analysis.frequency import term_frequency
from visualization.query import make_term_filter


def test_term_frequency(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    job = create_token_index_job(corpus)
    perform_indexing(job)

    client = elasticsearch(small_mock_corpus)
    index = 'test-small-mock-corpus-tokens'
    assert client.indices.exists(index=index)
    sleep(1)

    assert term_frequency(corpus, [], 'alice', 'content', None) == 1
    assert term_frequency(corpus, [], 'alice', 'content', 'clean') == 1
    assert term_frequency(
        corpus, [make_term_filter('genre', 'Children')], 'alice', 'content', None
    ) == 1
    assert term_frequency(
        corpus, [make_term_filter('genre', 'Romance')], 'alice', 'content', None
    ) == 0
    assert term_frequency(corpus, [], 'to', 'content', None) == 3
    assert term_frequency(corpus, [], 'to', 'content', 'clean') == 0

