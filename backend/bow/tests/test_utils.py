from bow.index_utils import has_bow_field
from es.search import get_index

def test_has_bow_field(
    small_mock_corpus, es_client, index_small_mock_corpus, index_small_mock_corpus_bow,
    basic_mock_corpus, index_basic_mock_corpus
):
    assert not has_bow_field(es_client, get_index(basic_mock_corpus), 'line')
    assert has_bow_field(es_client, get_index(small_mock_corpus), 'content')
