from addcorpus.models import Corpus
from corpora_test.small.small_mock_corpus import SPECS
from es.search import get_index
from bag_of_words.collect import collect_tokens, token_data
from bag_of_words.index_utils import bow_field_name

def test_collect_tokens(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(collect_tokens(corpus, index, 'content'))
    assert len(data) == SPECS['total_docs']
    assert sum(
        sum(term_counts.values())
        for _, term_counts in data
    ) == SPECS['total_words']

    _, terms = data[1]
    assert terms['truth'] == 1
    assert terms['a'] == 4


def iterate_tokens(data, content_field):
    return (token for _, doc in data for token in doc[bow_field_name(content_field)])


def test_token_docs(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(token_data(corpus, index, 'content'))

    assert sum(
        token[':count'] for token in iterate_tokens(data, 'content')
    ) == SPECS['total_words']

    singleton = [
        token for token in iterate_tokens(data, 'content')
        if token.get('content') == 'alice'
    ]
    assert len(singleton) == 1
    assert singleton[0][':token'] == 'alice'
    assert singleton[0][':count'] == 1

    assert sum(
        token[':count'] for token in iterate_tokens(data, 'content')
        if token.get('content') == 'to'
    ) == 3

