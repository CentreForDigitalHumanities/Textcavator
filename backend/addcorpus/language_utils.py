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

SUPPLEMENTARY_STOPWORDS_DIR = os.path.join(settings.BASE_DIR, 'addcorpus', 'stopword_data', 'supplementary_data')

def _stopwords_directory() -> str:
    stopwords_dir = os.path.join(settings.NLTK_DATA_PATH, 'corpora', 'stopwords')
    if not os.path.exists(stopwords_dir):
        nltk.download('stopwords', settings.NLTK_DATA_PATH)
    return stopwords_dir

def read_stopwords(key: str, source='nltk') -> List[str]:
    if source == 'nltk':
        dir = _stopwords_directory()
    else:
        dir = SUPPLEMENTARY_STOPWORDS_DIR

    path = os.path.join(dir, key)
    with open(path) as infile:
        words = [line.strip() for line in infile.readlines()]
        return words


def stopwords_filter(stopwords: List[str]) -> Dict:
    return {
        "type": "stop",
        'stopwords': stopwords
    }

# STEMMING

def stemmer_filter(language: str) -> Dict:
    return {
        "type": "stemmer",
        "language": language
    }
