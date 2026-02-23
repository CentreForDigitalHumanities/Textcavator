import pytest

from addcorpus.es_settings import es_settings
from addcorpus.language_utils import number_char_filter
from addcorpus.language_analysis import English, German

_english = English()
_german = German()

test_cases = {
    'single_language': {
        'languages': ['en'],
        'expected': {
            'char_filter': {
                'number_filter': number_char_filter()
            },
            'filter': {
                'stemmer_en': {'type': 'stemmer', 'language': 'english'},
                'stopwords_en': {'type': 'stop', 'stopwords': _english.stopwords()},
            },
            'analyzer': {
                'clean_en': _english._clean_analyzer(),
                'stemmed_en': _english._stemmed_analyzer(),
            }
        }
    },
    'multiple_languages': {
        'languages': ['en', 'de'],
        'expected': {
            'char_filter': {
                'number_filter': number_char_filter()
            },
            'filter': {
                'stemmer_de': {'type': 'stemmer', 'language': 'german'},
                'stopwords_de': {'type': 'stop', 'stopwords': _german.stopwords()},
                'stemmer_en': {'type': 'stemmer', 'language': 'english'},
                'stopwords_en': {'type': 'stop', 'stopwords': _english.stopwords()},
            },
            'analyzer': {
                'clean_de': _german._clean_analyzer(),
                'stemmed_de': _german._stemmed_analyzer(),
                'clean_en': _english._clean_analyzer(),
                'stemmed_en': _english._stemmed_analyzer()
            }
        }
    }
}

@pytest.mark.parametrize('test_config', list(test_cases.values()))
def test_es_settings(test_config):
    settings = es_settings(test_config['languages'])
    assert settings['analysis'] == test_config['expected']
