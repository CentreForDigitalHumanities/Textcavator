import pytest
import os

from addcorpus.models import Corpus
from addcorpus.reader import make_reader
from corpora_test.mixed_language.multilingual_mock_corpus import SPECS as ML_MOCK_CORPUS_SPECS
from download import tasks
from tag.models import Tag, TaggedDocument
from visualization.conftest import small_mock_corpus_specs, large_mock_corpus_specs
from visualization.query import MATCH_ALL

here = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture()
def csv_directory(settings, tmpdir):
    dir =  tmpdir.mkdir('/csv_files')
    settings.CSV_FILES_PATH = str(dir)
    return settings.CSV_FILES_PATH

@pytest.fixture(params=['small-mock-corpus', 'large-mock-corpus', 'multilingual-mock-corpus'])
def mock_corpus(request, small_mock_corpus, large_mock_corpus, ml_mock_corpus):
    'parametrised version of the mock corpus fixtures: runs with all'

    return request.param

@pytest.fixture()
def ml_mock_corpus_specs():
    return ML_MOCK_CORPUS_SPECS


@pytest.fixture()
def mock_corpus_specs(mock_corpus, small_mock_corpus, large_mock_corpus, ml_mock_corpus, small_mock_corpus_specs, large_mock_corpus_specs, ml_mock_corpus_specs):
    '''Return various specifications for the mock corpus (number of documents etc.)'''

    specs = {
        small_mock_corpus: small_mock_corpus_specs,
        large_mock_corpus: large_mock_corpus_specs,
        ml_mock_corpus: ml_mock_corpus_specs,
    }
    return specs[mock_corpus]

@pytest.fixture()
def index_mock_corpus(es_client, mock_corpus, index_small_mock_corpus, index_large_mock_corpus, index_ml_mock_corpus):
    yield mock_corpus

def all_results_request_json(mock_corpus, mock_corpus_specs):
    fields = mock_corpus_specs['fields']
    query = mock_corpus_specs['example_query']

    return {
        'corpus': mock_corpus,
        'es_query': MATCH_ALL,
        'fields': fields,
        'route': '/search/{};query={}'.format(mock_corpus, query)
    }

def save_all_results_csv(mock_corpus, mock_corpus_specs):
    request_json = all_results_request_json(mock_corpus, mock_corpus_specs)
    fake_id = mock_corpus + '_all_results'
    filename = tasks.make_download(request_json, fake_id)

    return filename

@pytest.fixture()
def small_mock_corpus_results_csv(small_mock_corpus, small_mock_corpus_specs, index_small_mock_corpus, csv_directory):
    return save_all_results_csv(small_mock_corpus, small_mock_corpus_specs)

@pytest.fixture()
def large_mock_corpus_results_csv(large_mock_corpus, large_mock_corpus_specs, index_large_mock_corpus, csv_directory):
    return save_all_results_csv(large_mock_corpus, large_mock_corpus_specs)

@pytest.fixture()
def ml_mock_corpus_results_csv(ml_mock_corpus, ml_mock_corpus_specs, index_ml_mock_corpus, csv_directory):
    return save_all_results_csv(ml_mock_corpus, ml_mock_corpus_specs)


@pytest.fixture()
def tag_mock_corpus_elasticsearch_results(tag_mock_corpus):
    corpus = Corpus.objects.get(name=tag_mock_corpus)
    docs = make_reader(corpus).documents()
    return [
        { '_id': doc['id'], '_source': doc }
        for doc in docs
    ]


@pytest.fixture()
def mock_corpus_results_csv(mock_corpus, small_mock_corpus, large_mock_corpus, ml_mock_corpus, small_mock_corpus_results_csv, large_mock_corpus_results_csv, ml_mock_corpus_results_csv):
    files = {
        small_mock_corpus: small_mock_corpus_results_csv,
        large_mock_corpus: large_mock_corpus_results_csv,
        ml_mock_corpus: ml_mock_corpus_results_csv,
    }

    return files[mock_corpus]
