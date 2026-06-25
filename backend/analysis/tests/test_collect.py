from addcorpus.models import Corpus
from corpora_test.small.small_mock_corpus import SPECS
from es.search import get_index
from analysis.collect import collect_tokens, token_docs

def test_collect_tokens(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(collect_tokens(corpus, index))
    assert len(data) == SPECS['total_docs']
    assert sum(sum(term_counts.values()) for _, term_counts, _ in data) == SPECS['total_words']

    field, terms, metadata = data[1]
    assert field == SPECS['content_field']
    assert terms['truth'] == 1
    assert terms['a'] == 4
    assert metadata['date'] == '1813-01-28'
    assert metadata['genre'] == 'Romance'


def test_token_docs(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(token_docs(corpus, index))
    assert len(data) == SPECS['total_words']

    singleton = [d for d in data if d['content:1'] == 'alice']
    assert len(singleton) == 1
    assert singleton[0]['genre'] == 'Children'

    multiple = [d for d in data if d['content:1'] == 'to']
    assert len(multiple) == 3
