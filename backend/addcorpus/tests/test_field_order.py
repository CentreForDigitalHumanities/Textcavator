from addcorpus.models import Corpus
from addcorpus.python_corpora.load_corpus import load_corpus_definition
from addcorpus.python_corpora.save_corpus import _save_corpus_configuration

def test_field_order_python_corpus(small_mock_corpus, admin_client):
    # check field order matches corpus definition
    response = admin_client.get('/api/corpus/')
    corpus_data = next(c for c in response.data if c['name'] == small_mock_corpus)
    field_names = [field['name'] for field in corpus_data['fields']]
    assert field_names == ['date', 'title', 'content', 'genre']

    # update field order
    corpus = Corpus.objects.get(name=small_mock_corpus)
    definition = load_corpus_definition(small_mock_corpus)
    definition.fields = list(reversed(definition.fields))
    _save_corpus_configuration(corpus, definition)

    # check order is updated
    response = admin_client.get('/api/corpus/')
    corpus_data = next(c for c in response.data if c['name'] == small_mock_corpus)

    field_names = [field['name'] for field in corpus_data['fields']]
    assert field_names == ['genre', 'content', 'title', 'date']
