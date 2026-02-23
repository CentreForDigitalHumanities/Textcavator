import warnings
from typing import Dict

from langcodes import standardize_tag

from addcorpus.language_utils import (get_language_key, get_nltk_stopwords, analyzer_name,
    stopwords_filter, stemmer_filter, number_char_filter, stemming_available)

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

        tag = standardize_tag(language, macro=True)

        if stopword_analysis or stemming_analysis:
            if not set_stopword_filter(settings, analyzer_name(stopword_filter_name, tag), tag):
                continue # skip languages for which we do not have a stopword list

            if stopword_analysis:
                set_clean_analyzer(
                    settings,
                    tag,
                    analyzer_name(stopword_filter_name, tag),
                    analyzer_name(clean_analyzer_name, tag),
                )
            if stemming_analysis:
                if not stemming_available(tag):
                    warnings.warn('You specified `stemming_analysis=True`, but \
                                      there is no stemmer available for this language')
                    continue
                set_stemmed_analyzer(
                    settings,
                    tag,
                    analyzer_name(stopword_filter_name, tag),
                    analyzer_name(stemmer_filter_name, tag),
                    analyzer_name(stemmed_analyzer_name, tag),
                )

    return settings


def make_stopword_filter(language):
    try:
        stopwords = get_nltk_stopwords(language)
        return stopwords_filter(stopwords)
    except:
        return None

def _standard_analyzer(language: str):
    '''
    Basic analyzer for a language.
    '''
    if language in ['zh', 'ja', 'ko']:
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
    return stemmer_filter(stemmer_language)

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
        "char_filter": { "number_filter": number_char_filter() }
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
