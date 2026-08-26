from time import sleep
from addcorpus.models import Corpus
from es.client import elasticsearch
from es.search import get_index
from bow.frequency import word_frequency, most_frequent_words
from visualization.query import MATCH_ALL, add_filter, make_term_filter


def test_word_frequency(small_mock_corpus, index_small_mock_corpus, index_small_mock_corpus_bow):
    corpus = Corpus.objects.get(name=small_mock_corpus)

    assert word_frequency(corpus, MATCH_ALL, 'alice', 'content', None) == 1
    assert word_frequency(corpus, MATCH_ALL, 'alice', 'content', 'clean') == 1
    query = add_filter(MATCH_ALL, make_term_filter('genre', 'Children'))
    assert word_frequency(
        corpus, query, 'alice', 'content', None
    ) == 1
    query = add_filter(MATCH_ALL, make_term_filter('genre', 'Romance'))
    assert word_frequency(
        corpus, query, 'alice', 'content', None
    ) == 0
    assert word_frequency(corpus, MATCH_ALL, 'to', 'content', None) == 3
    assert word_frequency(corpus, MATCH_ALL, 'to', 'content', 'clean') == 0

def test_most_frequent(small_mock_corpus, index_small_mock_corpus, index_small_mock_corpus_bow):
    corpus = Corpus.objects.get(name=small_mock_corpus)

    client = elasticsearch(small_mock_corpus)
    index = get_index(small_mock_corpus)
    assert client.indices.exists(index=index)
    sleep(1)

    results = most_frequent_words(corpus, MATCH_ALL, 'content')
    frequencies = { bucket['key']: bucket['token_count']['value'] for bucket in results['buckets'] }

    assert frequencies['alice'] == 1
    assert frequencies['to'] == 3
