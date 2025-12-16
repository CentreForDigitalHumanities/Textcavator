from addcorpus.models import Corpus
from es.search import get_index

def test_index_name_from_corpus_definition(db, basic_mock_corpus):
    corpus = Corpus.objects.get(name=basic_mock_corpus)
    assert get_index(basic_mock_corpus) == corpus.configuration.es_index

def test_generate_index_name_python_corpus(db, small_mock_corpus):
    assert get_index(small_mock_corpus) == f'test-{small_mock_corpus}'

def test_generate_index_name_db_corpus(db, json_mock_corpus):
    json_mock_corpus.configuration.es_index = ''
    json_mock_corpus.configuration.save()
    assert get_index(json_mock_corpus.name) == f'test-custom_{json_mock_corpus.pk}'

