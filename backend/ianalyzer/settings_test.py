from ianalyzer.settings import *

def mock_corpus_path(*path):
    return os.path.join(BASE_DIR, 'corpora_test', *path)

CORPORA = {
    'small-mock-corpus': mock_corpus_path('small', 'small_mock_corpus.py'),
    'large-mock-corpus': mock_corpus_path('large', 'large_mock_corpus.py'),
    'multilingual-mock-corpus': mock_corpus_path('mixed_language', 'multilingual_mock_corpus.py'),
    'times': os.path.join(BASE_DIR, 'corpora', 'times', 'times.py'),
    'media-mock-corpus': mock_corpus_path('media', 'media_mock_corpus.py'),
    'mock-csv-corpus': mock_corpus_path('basic', 'mock_csv_corpus.py'),
    'wordmodels-mock-corpus': mock_corpus_path('wordmodels', 'wm_mock_corpus.py'),
    'tagging-mock-corpus': mock_corpus_path('tag', 'tag_mock_corpus.py'),
    'annotated-mock-corpus': mock_corpus_path('named_entities', 'annotated_mock_corpus.py'),
}

TIMES_DATA = os.path.join(BASE_DIR, 'addcorpus', 'python_corpora', 'tests')
TIMES_ES_INDEX = 'test-times'

UBLAD_DATA = '' # necessary to make ublad test not fail

SERVERS['default']['index_prefix'] = 'test'

REST_FRAMEWORK.update(
    {
        "DEFAULT_THROTTLE_RATES": {
            "password": "2/minute",
            "registration": "2/minute",
            "download": "2/minute",
        }
    }
)
