import os
import warnings

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

def _nltk_stopwords_directory() -> str:
    nltk_stopwords_dir = os.path.join(settings.NLTK_DATA_PATH, 'corpora', 'stopwords')
    if not os.path.exists(nltk_stopwords_dir):
        nltk.download('stopwords', settings.NLTK_DATA_PATH)
    return nltk_stopwords_dir

def _nltk_stopwords_path(language_code: str):
    dir = _nltk_stopwords_directory()
    language = get_language_key(language_code)
    return os.path.join(dir, language)

def _supplementary_path(language_code: str):
    dir = os.path.join(settings.BASE_DIR, 'addcorpus', 'stopword_data', 'supplementary_data')
    language = get_language_key(language_code)
    return os.path.join(dir, language)

def stopwords_available(language_code: str) -> bool:
    if not language_code:
        return False
    nltk_path = _nltk_stopwords_path(language_code)
    supplementary_path = _supplementary_path(language_code)
    return True if (os.path.exists(nltk_path) or os.path.exists(supplementary_path)) else False

def get_stopwords(language_code):
    nltk_path = _nltk_stopwords_path(language_code)
    supplementary_path = _supplementary_path(language_code)
    if os.path.exists(nltk_path):
        with open(nltk_path) as infile:
            words = [line.strip() for line in infile.readlines()]
            return words
    elif os.path.exists(supplementary_path):
        with open(supplementary_path) as infile:
            words = [line.strip() for line in infile.readlines()]
            return words
    else:
        raise NotImplementedError('language {} has no stopwords list'.format(language_code))

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
                warnings.warn('You specified `stopword_analysis=True`, but \
                                      there are no stopwords available for this language')
                continue # skip languages for which we do not have a stopword list

            if stopword_analysis:
                set_clean_analyzer(
                    settings,
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
                    add_language_string(stopword_filter_name, language),
                    add_language_string(stemmer_filter_name, language),
                    add_language_string(stemmed_analyzer_name, language),
                    language
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
        stopwords = get_stopwords(language)
        return {
            "type": "stop",
            'stopwords': stopwords
        }
    except:
        return None

def make_clean_analyzer(stopword_filter_name):
    return {
        "tokenizer": "standard",
        "char_filter": ["number_filter"],
        "filter": ["lowercase", stopword_filter_name]
    }

def make_stemmer_filter(language):
    stemmer_language = get_language_key(language)
    return {
        "type": "stemmer",
        "language": stemmer_language
    }

def make_stemmed_analyzer(stopword_filter_name, stemmer_filter_name):
    return {
        "tokenizer": "standard",
        "char_filter": ["number_filter"],
        "filter": ["lowercase", stopword_filter_name, stemmer_filter_name]
    }

def get_stopwords_from_settings(es_settings, analyzer):
    try:
        # the name of the stopword filter is second in the list, after "lowercase"
        stopword_filter_name = es_settings['analysis']['analyzer'].get(
            analyzer).get('filter')[-1]
        token_filter = es_settings["analysis"]['filter'][stopword_filter_name]
        return token_filter['stopwords']
    except:
        return []

def set_stemmed_analyzer(settings, stopword_filter_name, stemmer_filter_name, stemmed_analyzer_name, language):
    filters = settings['analysis'].get('filter', {})
    filters.update({stemmer_filter_name: make_stemmer_filter(language)})
    settings['analysis']['filter'] = filters
    analyzers = settings['analysis'].get('analyzer')
    analyzers.update({stemmed_analyzer_name: make_stemmed_analyzer(stopword_filter_name, stemmer_filter_name)})
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

def set_clean_analyzer(settings, stopword_filter_name, clean_analyzer_name):
    clean_analyzer = make_clean_analyzer(stopword_filter_name)
    analyzers = settings['analysis'].get('analyzer', {})
    analyzers.update({clean_analyzer_name: clean_analyzer})
    settings["analysis"]['analyzer'] = analyzers
