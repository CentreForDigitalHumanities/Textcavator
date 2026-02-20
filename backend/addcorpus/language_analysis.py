from typing import Dict, List, Optional
from abc import ABC, abstractmethod

from langcodes import standardize_tag

from addcorpus.language_utils import (
    analyzer_name, stopwords_filter, stemmer_filter,
    number_char_filter, get_language_key, read_nltk_stopwords,
    stemming_available, stopwords_available
)

class LanguageAnalyzer(ABC):
    @property
    @abstractmethod
    def code(self) -> str:
        '''
        Standardised tag for the language
        '''
        pass

    @property
    def standard_analyzer_name(self) -> str:
        return 'standard'

    @property
    @abstractmethod
    def has_stopwords(self) -> bool:
        pass

    @property
    @abstractmethod
    def has_stemming(self) -> bool:
        pass

    def stopwords(self) -> Optional[List[str]]:
        '''
        Fetch list of stopwords for the language
        '''
        if self.has_stopwords:
            return read_nltk_stopwords(get_language_key(self))

    def char_filters(self) -> Dict:
        '''
        Custom char filters for the language
        '''
        return { 'number_filter': number_char_filter() }

    def token_filters(self) -> Dict:
        '''
        Custom token filters for the language
        '''
        filters = {}
        if self.has_stopwords:
            filters[self.stopwords_filter_name] = stopwords_filter(self.stopwords())
        if self.has_stemming:
            filters[self.stemmer_filter_name] = stemmer_filter(self.stemmer_filter_key)
        return filters

    def standard_analyzer(self) -> Optional[Dict]:
        '''
        Standard analyzer for text fields. Fields will use the built-in 'standard'
        analyzer by default. If you specify a custom analyzer here, it will be used
        instead.
        '''
        return None

    @property
    def stopwords_filter_name(self) ->str:
        return analyzer_name('stopwords', self.code)

    @property
    def clean_analyzer_name(self) -> str:
        return analyzer_name('clean', self.code)

    def clean_analyzer(self) -> Optional[Dict]:
        '''
        Analyzer that removes stopwords, if supported. Will be used in a 'clean'
        multifield.
        '''
        if self.has_stopwords:
            return {
                'tokenizer': 'standard',
                'char_filter': ['number_filter'],
                'filter': ['lowercase', self.stopwords_filter_name]
            }

    @property
    def stemmer_filter_name(self) -> str:
        return analyzer_name('stemmer', self.code)

    @property
    def stemmer_filter_key(self) -> Optional[str]:
        if self.has_stemming:
            return get_language_key(self.code)

    @property
    def stemmed_analyzer_name(self) -> Optional[str]:
        if self.has_stemming:
            return analyzer_name('stemmed', self.code)

    def stemmed_analyzer(self) -> Optional[Dict]:
        '''
        Analyzer that removes stopwords and stems tokens, if supported. Will be used
        in a 'stemmed' multifield.
        '''
        if self.has_stemming:
            analyzer = self.clean_analyzer()
            analyzer['filter'].append(self.stemmer_filter_name)
            return analyzer


class LegacyAnalyzer(LanguageAnalyzer):
    def __init__(self, code: str):
        self.code = standardize_tag(code)

    @property
    def has_stopwords(self):
        return stopwords_available(self.code)

    @property
    def has_stemming(self):
        return stemming_available(self.code)


class English(LanguageAnalyzer):
    code = 'en'
    has_stopwords = True
    has_stemming = True


class Dutch(LanguageAnalyzer):
    code = 'nl'
    has_stopwords = True
    has_stemming = True


class French(LanguageAnalyzer):
    code = 'fr'
    has_stopwords = True
    has_stemming = True

    def token_filters(self):
        filters = super().token_filters()
        filters['french_elision'] = {
            'type': 'elision',
            'articles_case': True,
            'articles': [
                'l', 'm', 't', 'qu', 'n', 's', 'j', 'd', 'c', 'jusqu', 'quoiqu',
                'lorsqu', 'puisqu'
            ]
        },
        return filters

    def standard_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': [
                'french_elision',
                'lowercase',
            ]
        }

    def clean_analyzer(self):
        return {
            'tokenizer': 'standard',
            'char_filter': ['number_filter'],
            'filter': [
                'french_elision',
                'lowercase',
                self.stopwords_filter_name,
            ]
        }


class German(LanguageAnalyzer):
    code = 'de'
    has_stopwords = True
    has_stemming = True

    def standard_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': [
                'lowercase',
                'german_normalization',
            ]
        }

    def clean_analyzer(self):
        return {
            'tokenizer': 'standard',
            'char_filter': ['number_filter'],
            'filter': [
                'lowercase',
                'german_normalization',
                self.stopwords_filter_name,
            ]
        }


class Chinese(LanguageAnalyzer):
    code = 'zh'
    has_stopwords = True
    has_stemming = False

    def standard_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': [
                'cjk_width',
                'lowercase',
            ]
        }
