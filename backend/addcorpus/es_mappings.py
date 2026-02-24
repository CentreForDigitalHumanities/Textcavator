from typing import Dict, Optional
from addcorpus.language_analysis import get_analyzer

def primary_mapping_type(es_mapping: Dict) -> str:
    return es_mapping.get('type', None)


def main_content_mapping(
    token_counts=True, stopword_analysis=False, stemming_analysis=False,
    language: Optional[str] = None
):
    '''
    Mapping for the main content field. Options:

    - `token_counts`: enables aggregations for the total number of words. Used for relative term frequencies.
    - `stopword_analysis`: enables analysis using stopword removal, if available for the language.
    - `stemming_analysis`: enables analysis using stemming, if available for the language.
    - `language`: language (IETF tag) of the field contents
    '''

    analyzer = get_analyzer(language)
    mapping = {
        'type': 'text',
        'analyzer': analyzer.standard_analyzer_name,
        'term_vector': 'with_positions_offsets'
    }

    if any([token_counts, stopword_analysis, stemming_analysis]):
        multifields = {}
        if token_counts:
            multifields['length'] = {
                'type':     'token_count',
                'analyzer': analyzer.standard_analyzer_name
            }

        if stopword_analysis and analyzer.has_stopwords:
            multifields['clean'] = {
                'type': 'text',
                'analyzer': analyzer.clean_analyzer_name,
                'term_vector': 'with_positions_offsets' # include character positions for highlighting
            }
        if stemming_analysis and analyzer.has_stemming:
            multifields['stemmed'] = {
                'type': 'text',
                'analyzer': analyzer.stemmed_analyzer_name,
                'term_vector': 'with_positions_offsets',
            }
        mapping['fields'] = multifields

    return mapping


def text_mapping(language: Optional[str] = None):
    '''
    Mapping for text fields that are not the main content. Performs standard analysis for full-text
    search, but does not support other analysis options.
    '''

    analyzer = get_analyzer(language)

    return {
        'type': 'text',
        'analyzer': analyzer.standard_analyzer_name,
    }

def keyword_mapping(enable_full_text_search = False, language: Optional[str] = None):
    '''
    Mapping for keyword fields. Keyword fields allow filtering and histogram visualisations.

    They do not have full text search by default. Set `enable_full_text_search = True` if you want this field to be searchable as well as filterable.
    '''

    mapping = {
        'type': 'keyword'
    }
    if enable_full_text_search:
        mapping['fields'] = {
            'text': text_mapping(language)
        }

    return mapping

def date_mapping(format='yyyy-MM-dd'):
    return {
        'type': 'date',
        'format': format
    }

def date_estimate_mapping(format='yyyy-MM-dd'):
    return {
        'type': 'date_range',
        'format': format
    }

def int_mapping():
    return {
        'type': 'integer'
    }

def float_mapping():
    return {
        'type': 'float'
    }

def bool_mapping():
    return {'type': 'boolean'}

def geo_mapping():
    return {'type': 'geo_point'}


def non_indexed_text_mapping():
    return {'type': 'text', 'index': False}
