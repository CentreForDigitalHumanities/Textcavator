import os
from django.conf import settings
import pytest

from addcorpus.models import Corpus
from addcorpus.reader import make_reader
from addcorpus.validation.indexing import CorpusNotIndexableError

def _test_reader_output(docs):
    assert len(docs) == 10
    assert docs[0] == {
        'character': 'HAMLET',
        'line': "Whither wilt thou lead me? Speak, I\'ll go no further."
    }


def test_make_reader_python(basic_mock_corpus):
    corpus = Corpus.objects.get(name=basic_mock_corpus)
    reader = make_reader(corpus)
    docs = list(reader.documents())
    _test_reader_output(docs)


def test_make_reader_json(json_mock_corpus):
    data_dir = os.path.join(settings.BASE_DIR, 'corpora_test', 'basic', 'source_data')
    json_mock_corpus.configuration.data_directory = data_dir
    json_mock_corpus.configuration.save()
    reader = make_reader(json_mock_corpus)
    docs = list(reader.documents())
    _test_reader_output(docs)


def test_reader_uses_directory(json_mock_corpus: Corpus, small_mock_corpus: str):
    '''Test that a data_directory takes precedence over CorpusDataFile'''
    other_corpus = Corpus.objects.get(name=small_mock_corpus)
    json_mock_corpus.configuration.data_directory = other_corpus.configuration.data_directory
    json_mock_corpus.configuration.save()

    reader = make_reader(json_mock_corpus)
    docs = list(reader.documents())
    with pytest.raises(AssertionError):
        _test_reader_output(docs)


def test_reader_validates_directory(json_mock_corpus: Corpus, tmp_path):
    # should run without error
    make_reader(json_mock_corpus)

    json_mock_corpus.configuration.data_directory = tmp_path / 'doesnotexist'
    json_mock_corpus.configuration.save()

    with pytest.raises(CorpusNotIndexableError):
        reader = make_reader(json_mock_corpus)
