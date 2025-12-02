import sys
import pytest
from django.conf import settings
from corpora_test.basic.mock_csv_corpus import MockCSVCorpus
from addcorpus.models import Corpus, CorpusConfiguration
from addcorpus.python_corpora.save_corpus import (_save_field_in_database,
    load_and_save_all_corpora, _save_or_skip_corpus
)

pytestmark = [
    pytest.mark.filterwarnings("ignore:Corpus has no 'id' field"),
    pytest.mark.filterwarnings('ignore:.* text search for keyword fields without text analysis')
]

def test_saved_corpora(db, save_mock_corpora):
    '''
    Assert that all the mock corpora are saved to the database
    during test setup
    '''

    configured = settings.CORPORA

    for corpus_name in configured:
        assert Corpus.objects.filter(name=corpus_name).exists()
        corpus = Corpus.objects.get(name=corpus_name)
        conf = corpus.configuration_obj
        assert corpus.configuration_obj
        assert corpus.active

    assert Corpus.objects.filter(
        has_python_definition=True).count() == len(configured)
    assert CorpusConfiguration.objects.filter(
        corpus__has_python_definition=True).count() == len(configured)

def test_no_errors_when_saving_corpora(db, capsys):
    # try running the save function
    # sys.stdout/stderr needs to be passed explicitly for capture to work
    load_and_save_all_corpora(verbose=True, stdout=sys.stdout, stderr=sys.stderr)
    captured = capsys.readouterr()

    # assert no errors are logged
    assert not captured.err

    # assert stdout contains only success statements
    for line in captured.out.split('\n'):
        assert line == '' or line.startswith('Saved corpus:')

def test_saving_broken_corpus(db, basic_mock_corpus):
    corpus = Corpus.objects.get(name=basic_mock_corpus)
    corpus_def = MockCSVCorpus()

    corpus_def.min_date = 'Not a valid date'

    _save_or_skip_corpus(basic_mock_corpus, corpus_def)

    corpus.refresh_from_db()
    # expect the the corpus to be inactive now
    assert not corpus.active
    assert corpus.has_python_definition

def test_remove_corpus_from_settings(db, settings, basic_mock_corpus):
    corpus = Corpus.objects.get(name=basic_mock_corpus)
    assert corpus.active
    assert corpus.has_python_definition

    path = settings.CORPORA.pop(basic_mock_corpus)
    load_and_save_all_corpora()
    corpus.refresh_from_db()
    assert not corpus.active
    assert not corpus.has_python_definition

    settings.CORPORA[basic_mock_corpus] = path
    load_and_save_all_corpora()
    corpus.refresh_from_db()
    assert corpus.active
    assert corpus.has_python_definition

@pytest.fixture()
def deactivated_corpus(basic_mock_corpus):
    corpus = Corpus.objects.get(name=basic_mock_corpus)
    corpus.active = False
    corpus.save()

    yield corpus

    corpus.active = True
    corpus.save()

def test_save_field_definition(db, basic_mock_corpus, deactivated_corpus):
    corpus = Corpus.objects.get(name=basic_mock_corpus)
    corpus_conf = corpus.configuration
    corpus_def = MockCSVCorpus()

    corpus_conf.fields.all().delete()

    for index, field_def in enumerate(corpus_def.fields):
        field = _save_field_in_database(field_def, corpus_conf, index)
        assert field
        assert field.name == field_def.name

def test_save_corpus_purity(db, basic_mock_corpus):
    '''
    Test that saved corpus configurations only depend
    on the definition at that time, not on the currently
    saved state
    '''

    corpus = Corpus.objects.get(name=basic_mock_corpus)
    corpus_def = MockCSVCorpus()

    corpus_def.es_alias = 'test'
    _save_or_skip_corpus(basic_mock_corpus, corpus_def)
    corpus.refresh_from_db()
    assert corpus.configuration.es_alias == 'test'

    corpus_def.es_alias = None
    _save_or_skip_corpus(basic_mock_corpus, corpus_def)
    corpus.refresh_from_db()
    assert not corpus.configuration.es_alias


def test_has_named_entities(db, annotated_mock_corpus, index_annotated_mock_corpus):
    load_and_save_all_corpora() # corpora must be refreshed after indexing to detect annotations
    conf = CorpusConfiguration.objects.get(corpus__name=annotated_mock_corpus)
    assert conf.has_named_entities
