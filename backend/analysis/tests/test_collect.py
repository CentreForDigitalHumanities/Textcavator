from addcorpus.models import Corpus
from corpora_test.small.small_mock_corpus import SPECS
from es.search import get_index
from analysis.collect import collect_tokens, token_docs

def test_collect_tokens(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(collect_tokens(corpus, index))
    assert len(data) == SPECS['total_docs']
    assert sum(
        sum(term_counts.values())
        for _, term_counts, _, _ in data
    ) == SPECS['total_words']

    field, terms, metadata, doc_id = data[1]
    assert field == SPECS['content_field']
    assert terms['truth'] == 1
    assert terms['a'] == 4
    assert metadata['date'] == '1813-01-28'
    assert metadata['genre'] == 'Romance'


def test_token_docs(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(token_docs(corpus, index))

    assert sum(token[':count'] for token in data) == SPECS['total_words']

    singleton = [d for d in data if d.get('content') == 'alice']
    assert len(singleton) == 1
    assert singleton[0][':token'] == 'alice'
    assert singleton[0][':count'] == 1
    assert singleton[0]['genre'] == 'Children'

    assert sum(d[':count'] for d in data if d.get('content') == 'to') == 3

