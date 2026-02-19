import os
from typing import List, Dict

from django.conf import settings
from langcodes import Language, standardize_tag
import nltk

def analyzer_name(analysis_type: str, language: str) -> str:
    return '{}_{}'.format(analysis_type, language) if language else analysis_type


def number_char_filter():
    return {
        "type":"pattern_replace",
        "pattern":"\\d+",
        "replacement":""
    }

def get_language_key(language_code):
    '''
    Get the nltk stopwords file / elasticsearch stemmer name for a language code

    E.g. 'en' -> 'english'
    '''

    return Language.make(standardize_tag(language_code)).display_name().lower()

# STOPWORDS

def _stopwords_directory() -> str:
    stopwords_dir = os.path.join(settings.NLTK_DATA_PATH, 'corpora', 'stopwords')
    if not os.path.exists(stopwords_dir):
        nltk.download('stopwords', settings.NLTK_DATA_PATH)
    return stopwords_dir

def _stopwords_path(language_code: str):
    dir = _stopwords_directory()
    language = get_language_key(language_code)
    return os.path.join(dir, language)

def stopwords_available(language_code: str) -> bool:
    if not language_code:
        return False
    path = _stopwords_path(language_code)
    return os.path.exists(path)

def get_nltk_stopwords(language_code):
    path = _stopwords_path(language_code)

    if os.path.exists(path):
        with open(path) as infile:
            words = [line.strip() for line in infile.readlines()]
            return words
    else:
        raise NotImplementedError('language {} has no nltk stopwords list'.format(language_code))

def read_nltk_stopwords(key: str) -> List[str]:
    dir = _stopwords_directory()
    path = os.path.join(dir, key)

    if os.path.exists(path):
        with open(path) as infile:
            words = [line.strip() for line in infile.readlines()]
            return words


def stopwords_filter(stopwords: List[str]) -> Dict:
    return {
        "type": "stop",
        'stopwords': stopwords
    }

# STEMMING

# available Elasticsearch stemmers [https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-stemmer-tokenfilter.html]
AVAILABLE_ES_STEMMERS = ['arabic', 'armenian', 'basque', 'bengali', 'brazilian',
                         'bulgarian', 'catalan', 'cjk', 'czech', 'danish', 'dutch',
                         'english', 'estonian', 'finnish', 'french', 'galician',
                         'german', 'greek', 'hindi', 'hungarian', 'indonesian',
                         'irish', 'italian', 'latvian', 'lithuanian', 'norwegian',
                         'persian', 'portuguese', 'romanian', 'russian', 'sorani',
                         'spanish', 'swedish', 'turkish', 'thai']


def stemming_available(language_code: str) -> bool:
    '''
    Check whether stemming is supported for a language.

    Parameters:
        language: an ISO-639 language code

    Returns:
        whether elasticsearch supports stemming analysis in this language.
    '''
    if not language_code:
        return False
    return get_language_key(language_code) in AVAILABLE_ES_STEMMERS


def stemmer_filter(language: str) -> Dict:
    return {
        "type": "stemmer",
        "language": language
    }
