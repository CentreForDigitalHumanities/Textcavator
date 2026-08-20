from addcorpus.models import Corpus
from corpora_test.small.small_mock_corpus import SPECS
from es.search import get_index
from bow.collect import collect_tokens, token_docs
from bow.index_utils import bow_field_name

def test_collect_tokens(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(collect_tokens(corpus, index))
    assert len(data) == SPECS['total_docs']
    assert sum(
        sum(stats[':count'] for stats in term_counts.values())
        for _, term_counts, _, _ in data
    ) == SPECS['total_words']

    field, terms, metadata, doc_id = data[1]
    assert field == SPECS['content_field']
    assert terms['truth'] == {':count': 1, ':total_count': 1}
    assert terms['that'] == {':count': 1, ':total_count': 2}
    assert terms['a'] == {':count': 4, ':total_count': 4}
    assert metadata['date'] == '1813-01-28'
    assert metadata['genre'] == 'Romance'


def iterate_tokens(data, content_field):
    return (token for doc in data for token in doc[bow_field_name(content_field)])


def test_token_docs(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(token_docs(corpus, index))

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


def test_token_threshold(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(token_docs(corpus, index, threshold=2))

    assert sum(
        token[':count'] for token in iterate_tokens(data, 'content')
        if token.get('content') == 'alice'
    ) == 0
    assert sum(
        token[':count'] for token in iterate_tokens(data, 'content')
        if token.get('content') == 'to'
    ) == 3
