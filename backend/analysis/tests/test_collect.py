from addcorpus.models import Corpus
from corpora_test.small.small_mock_corpus import SPECS
from es.search import get_index
from analysis.collect import collect_tokens, token_docs

def test_collect_tokens(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(collect_tokens(corpus, index))
    assert len(data) == SPECS['total_docs'] * 2 # 2 fields per document (standard + cleaned)
    assert sum(
        sum(term_counts.values())
        for _, multifield, term_counts, _ in data
        if not multifield
    ) == SPECS['total_words']

    field, multifield, terms, metadata = data[2]
    assert field == SPECS['content_field']
    assert multifield == None
    assert terms['truth'] == 1
    assert terms['a'] == 4
    assert metadata['date'] == '1813-01-28'
    assert metadata['genre'] == 'Romance'


def test_token_docs(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    index = get_index(small_mock_corpus)
    data = list(token_docs(corpus, index))

    assert sum(
        1 for token in data if token.get('content:1')
    ) == SPECS['total_words']

    singleton = [d for d in data if d.get('content:1') == 'alice']
    assert len(singleton) == 1
    assert singleton[0]['genre'] == 'Children'

    assert sum(1 for d in data if d.get('content:clean:1') == 'alice') == 1
    assert sum(1 for d in data if d.get('content:1') == 'to') == 3
    assert sum(1 for d in data if d.get('content:clean:1') == 'to') == 0

