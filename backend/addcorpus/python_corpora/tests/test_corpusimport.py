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
    assert 'mock_csv_corpus.py' in os.listdir(path)
    assert 'source_data' in os.listdir(path)
