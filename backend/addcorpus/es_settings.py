import os
import warnings
from typing import Dict

from django.conf import settings
from langcodes import Language, standardize_tag
import nltk

# available Elasticsearch stemmers [https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-stemmer-tokenfilter.html]
AVAILABLE_ES_STEMMERS = ['arabic', 'armenian', 'basque', 'bengali', 'brazilian',
                         'bulgarian', 'catalan', 'cjk', 'czech', 'danish', 'dutch',
                         'english', 'estonian', 'finnish', 'french', 'galician',
                         'german', 'greek', 'hindi', 'hungarian', 'indonesian',
                         'irish', 'italian', 'latvian', 'lithuanian', 'norwegian',
                         'persian', 'portuguese', 'romanian', 'russian', 'sorani',
                         'spanish', 'swedish', 'turkish', 'thai']

def get_language_key(language_code):
    '''
    Get the nltk stopwords file / elasticsearch stemmer name for a language code

    E.g. 'en' -> 'english'
    '''

    return Language.make(standardize_tag(language_code)).display_name().lower()

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

def add_language_string(name, language):
    return '{}_{}'.format(name, language) if language else name

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

def es_settings(languages=[], stopword_analysis=False, stemming_analysis=False):
    '''
    Make elasticsearch settings json for a corpus index. Options:
    - `languages`: array of language codes. See addcorpus.constants for options, and which languages support stopwords/stemming
    - `stopword_analysis`: set to True to add an analyzer that removes stopwords.
    - `stemming_analysis`: set to True to add an analyzer that removes stopwords and performs stemming.
    '''
    settings = {'index': {'number_of_shards': 1, 'number_of_replicas': 1}}
    stopword_filter_name = 'stopwords'
    clean_analyzer_name = 'clean'
    stemmer_filter_name = 'stemmer'
    stemmed_analyzer_name = 'stemmed'

    set_char_filter(settings)

    for language in languages:
        # do not attach language isocodes if there is just one language

        if stopword_analysis or stemming_analysis:
            if not set_stopword_filter(settings, add_language_string(stopword_filter_name, language), language):
                continue # skip languages for which we do not have a stopword list

            if stopword_analysis:
                set_clean_analyzer(
                    settings,
                    language,
                    add_language_string(stopword_filter_name, language),
                    add_language_string(clean_analyzer_name, language),
                )
            if stemming_analysis:
                if not stemming_available(language):
                    warnings.warn('You specified `stemming_analysis=True`, but \
                                      there is no stemmer available for this language')
                    continue
                set_stemmed_analyzer(
                    settings,
                    language,
                    add_language_string(stopword_filter_name, language),
                    add_language_string(stemmer_filter_name, language),
                    add_language_string(stemmed_analyzer_name, language),
                )

    return settings

def number_filter():
    return {
        "type":"pattern_replace",
        "pattern":"\\d+",
        "replacement":""
    }

def make_stopword_filter(language):
    try:
        stopwords = get_nltk_stopwords(language)
        return {
            "type": "stop",
            'stopwords': stopwords
        }
    except:
        return None

def _standard_analyzer(language: str):
    '''
    Basic analyzer for a language.
    '''
    if language in ['zho', 'jpn', 'kor']:
        return {
            'tokenizer': 'standard',
            'filter': [
                'cjk_width',
                'lowercase',
            ]
        }
    else:
        return {
            'tokenizer': 'standard',
            'char_filter': ['number_filter'],
            'filter': ['lowercase']
        }

def make_clean_analyzer(language: str, stopword_filter_name: str) -> Dict:
    analyzer = _standard_analyzer(language)
    analyzer['filter'].append(stopword_filter_name)
    return analyzer


def make_stemmer_filter(language):
    stemmer_language = get_language_key(language)
    return {
        "type": "stemmer",
        "language": stemmer_language
    }

def make_stemmed_analyzer(
    language: str, stopword_filter_name: str, stemmer_filter_name: str
) -> Dict:
    analyzer = make_clean_analyzer(language, stopword_filter_name)
    analyzer['filter'].append(stemmer_filter_name)
    return analyzer


def get_stopwords_from_settings(es_settings, analyzer):
    try:
        # the name of the stopword filter is second in the list, after "lowercase"
        stopword_filter_name = es_settings['analysis']['analyzer'].get(
            analyzer).get('filter')[-1]
        token_filter = es_settings["analysis"]['filter'][stopword_filter_name]
        return token_filter['stopwords']
    except:
        return []

def set_stemmed_analyzer(
        settings: Dict,
        language: str,
        stopword_filter_name: str,
        stemmer_filter_name: str,
        stemmed_analyzer_name: str,
) -> None:
    filters = settings['analysis'].get('filter', {})
    filters.update({stemmer_filter_name: make_stemmer_filter(language)})
    settings['analysis']['filter'] = filters
    analyzers = settings['analysis'].get('analyzer')
    analyzers.update({stemmed_analyzer_name: make_stemmed_analyzer(
        language, stopword_filter_name, stemmer_filter_name)})
    settings['analysis']['analyzer'] = analyzers

def set_char_filter(settings):
    settings["analysis"] = {
        "char_filter": { "number_filter": number_filter() }
    }

def set_stopword_filter(settings, stopword_filter_name, language):
    stopword_filter = make_stopword_filter(language)
    if not stopword_filter:
        return False
    filters = settings['analysis'].get('filter', {})
    filters.update({
        stopword_filter_name: stopword_filter
    })
    settings['analysis']['filter'] = filters
    return True

def set_clean_analyzer(
    settings: Dict,
    language: str,
    stopword_filter_name: str,
    clean_analyzer_name: str,
) -> None:
    clean_analyzer = make_clean_analyzer(language, stopword_filter_name)
    analyzers = settings['analysis'].get('analyzer', {})
    analyzers.update({clean_analyzer_name: clean_analyzer})
    settings["analysis"]['analyzer'] = analyzers
