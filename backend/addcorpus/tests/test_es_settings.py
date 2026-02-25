import pytest

from addcorpus.es_settings import es_settings
from addcorpus.language_utils import number_char_filter
from addcorpus.language_analysis import Dutch, Spanish

_dutch = Dutch()
_spanish = Spanish()

test_cases = {
    'single_language': {
        'languages': ['nl'],
        'expected': {
            'char_filter': {
                'number_filter': number_char_filter()
            },
            'filter': {
                'stemmer_nl': {'type': 'stemmer', 'language': 'dutch'},
                'stopwords_nl': {'type': 'stop', 'stopwords': _dutch.stopwords()},
            },
            'analyzer': {
                'clean_nl': _dutch._clean_analyzer(),
                'stemmed_nl': _dutch._stemmed_analyzer(),
            }
        }
    },
    'multiple_languages': {
        'languages': ['nl', 'es'],
        'expected': {
            'char_filter': {
                'number_filter': number_char_filter()
            },
            'filter': {
                'stemmer_es': {'type': 'stemmer', 'language': 'light_spanish'},
                'stopwords_es': {'type': 'stop', 'stopwords': _spanish.stopwords()},
                'stemmer_nl': {'type': 'stemmer', 'language': 'dutch'},
                'stopwords_nl': {'type': 'stop', 'stopwords': _dutch.stopwords()},
            },
            'analyzer': {
                'clean_es': _spanish._clean_analyzer(),
                'stemmed_es': _spanish._stemmed_analyzer(),
                'clean_nl': _dutch._clean_analyzer(),
                'stemmed_nl': _dutch._stemmed_analyzer()
            }
        }
    }
}

@pytest.mark.parametrize('test_config', list(test_cases.values()))
def test_es_settings(test_config):
    settings = es_settings(test_config['languages'])
    assert settings['analysis'] == test_config['expected']
