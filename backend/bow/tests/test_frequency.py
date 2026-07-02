from time import sleep
from addcorpus.models import Corpus
from bow.create_index_job import create_bow_index_job
from es.client import elasticsearch
from indexing.run_job import perform_indexing
from bow.frequency import word_frequency, most_frequent_words
from visualization.query import make_term_filter


def test_word_frequency(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    job = create_bow_index_job(corpus)
    perform_indexing(job)

    client = elasticsearch(small_mock_corpus)
    index = 'test-small-mock-corpus.bow'
    assert client.indices.exists(index=index)
    sleep(1)

    assert word_frequency(corpus, [], 'alice', 'content', None) == 1
    assert word_frequency(corpus, [], 'alice', 'content', 'clean') == 1
    assert word_frequency(
        corpus, [make_term_filter('genre', 'Children')], 'alice', 'content', None
    ) == 1
    assert word_frequency(
        corpus, [make_term_filter('genre', 'Romance')], 'alice', 'content', None
    ) == 0
    assert word_frequency(corpus, [], 'to', 'content', None) == 3
    assert word_frequency(corpus, [], 'to', 'content', 'clean') == 0

def test_most_frequent(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    job = create_bow_index_job(corpus)
    perform_indexing(job)

    client = elasticsearch(small_mock_corpus)
    index = 'test-small-mock-corpus.bow'
    assert client.indices.exists(index=index)
    sleep(1)

    results = most_frequent_words(corpus, [], 'content')
    frequencies = { bucket['key']: bucket['token_count']['value'] for bucket in results['buckets'] }

    assert frequencies['alice'] == 1
    assert frequencies['to'] == 3
