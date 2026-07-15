import os
import pytest
from addcorpus.python_corpora import load_corpus
from addcorpus.models import Corpus

def test_key_error(db, settings):
    ''' Verify that exception is correctly raised
    - in case the config.CORPORA variable is empty
    '''

    settings.CORPORA = {}

    with pytest.raises(KeyError) as e:
        corpora = load_corpus.load_all_corpus_definitions()
        corpora['times']

def test_import_error(db, settings):
    ''' Verify that exceptions is correctly raised
    - in case the path in config.CORPORA is faulty
    '''

    settings.CORPORA = {'times2': 'somewhere.times.times.Times'}

    with pytest.raises(ModuleNotFoundError) as e:
        load_corpus.load_corpus_definition('times2')

    # corpus should not be included when
    # loading all corpora
    corpora = load_corpus.load_all_corpus_definitions()
    assert 'times2' not in corpora
    assert not Corpus.objects.filter(name='times2')


def test_corpus_dir(db, settings, basic_mock_corpus):
    path = load_corpus.corpus_dir(basic_mock_corpus)
    assert os.path.isabs(path)
    assert 'corpus.py' in os.listdir(path)
    assert 'source_data' in os.listdir(path)


def test_corpus_settings(db, settings):
    '''Test configuration using CORPUS_SETTINGS'''
    settings.CORPORA = {
        'example': 'corpora_test.basic.mock_csv_corpus.MockCSVCorpus',
        'example-2':  'corpora_test.basic.mock_csv_corpus.MockCSVCorpus',
    }
    settings.CORPUS_SETTINGS = {
        'example-2': {
            'title': 'Different title'
        }
    }
    corpora = load_corpus.load_all_corpus_definitions()
    assert len(corpora) == 2
    assert corpora['example'].title == 'Example'
    assert corpora['example-2'].title == 'Different title'


def test_corpus_property_override(db, settings):
    '''
    Test that CORPUS_SETTINGS also works when the original value is a
    property without a setter (e.g. in CorpusDefinition itself)
    '''
    settings.CORPORA = {
        'test': 'addcorpus.python_corpora.corpus.CorpusDefinition',
    }
    settings.CORPUS_SETTINGS = {
        'test': {
            'title': 'Example',
            'description': 'Description',
            'min_date': 1900,
            'max_date': 2000,
            'category': 'other',
            'fields': [],
        }
    }
    corpora = load_corpus.load_all_corpus_definitions()
    assert corpora['test'].title == 'Example'

