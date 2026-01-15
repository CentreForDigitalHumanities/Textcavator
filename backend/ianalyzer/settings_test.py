from ianalyzer.settings import *

def mock_corpus_path(*path):
    return os.path.join(BASE_DIR, 'corpora_test', *path)

CORPORA = {
    'small-mock-corpus': 'corpora_test.small.small_mock_corpus.SmallMockCorpus',
    'large-mock-corpus': 'corpora_test.large.large_mock_corpus.LargeMockCorpus',
    'multilingual-mock-corpus': 'corpora_test.mixed_language.multilingual_mock_corpus.MultilingualMockCorpus',
    'times': 'corpora.times.times.Times',
    'media-mock-corpus': 'corpora_test.media.media_mock_corpus.MediaMockCorpus',
    'mock-csv-corpus': 'corpora_test.basic.mock_csv_corpus.MockCSVCorpus',
    'wordmodels-mock-corpus': 'corpora_test.wordmodels.wm_mock_corpus.WordmodelsMockCorpus',
    'tagging-mock-corpus': 'corpora_test.tag.tag_mock_corpus.TaggingMockCorpus',
    'annotated-mock-corpus': 'corpora_test.named_entities.annotated_mock_corpus.AnnotatedMockCorpus',
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
