from typing import Dict, List, Optional, Type
from abc import ABC, abstractmethod

from langcodes import closest_match

from addcorpus.language_utils import (
    analyzer_name, stopwords_filter, stemmer_filter,
    number_char_filter, get_language_key, read_nltk_stopwords,
)

class LanguageAnalyzer(ABC):
    '''
    Base class for language analyzers. Create subclass to implement a specific language.

    The purpose of this class is to hold the configuration for a language, mostly
    regarding the setup of text analysis in Elasticsearch. See

    https://www.elastic.co/guide/en/elasticsearch/reference/8.17/analysis.html

    for documentation. In some cases, the language configuration can also be used
    by other modules, e.g. to get the stopwords list.

    Miminum required attributes:
        code: the IETF tag for the language.
        has_stopwords: indicates support for stopwords filtering
        has_stemming: indiciates support for stemming in addition to stopword filtering

    If you set `has_stopwords` or `has_stemming` to `True`, the class will generate
    analyzers based on the NLTK stopwords corpus, a simple number filter, and built-in
    stemmers from Elasticsearch. You may need to override these methods, e.g. to use a
    custom stopwords list or specify the stemmer.

    It is worth looking at the built-in language analyzers from Elasticsearch:

    https://www.elastic.co/guide/en/elasticsearch/reference/8.17/analysis-lang-analyzer.html

    These may include other language-specific filters that can be useful.
    '''

    @property
    @staticmethod
    @abstractmethod
    def code(self) -> str:
        '''
        Standardised tag for the language
        '''
        pass

    @property
    @abstractmethod
    def has_stopwords(self) -> bool:
        '''
        Whether the language supports stopword filtering.
        '''
        pass

    @property
    @abstractmethod
    def has_stemming(self) -> bool:
        '''
        Whether the language supports stemming *in addition to* stopword filtering.
        '''
        pass


    def char_filters(self) -> Dict:
        '''
        Custom char filters for the language. Will be added in ES index settings.
        '''
        return { 'number_filter': number_char_filter() }

    def token_filters(self) -> Dict:
        '''
        Custom token filters for the language. Will be added in ES index settings.
        '''
        filters = {}
        if self.has_stopwords:
            filters[self._stopwords_filter_name] = stopwords_filter(self.stopwords())
        if self.has_stemming:
            filters[self._stemmer_filter_name] = stemmer_filter(self._stemmer_filter_language)
        return filters


    def analyzers(self) -> Dict:
        '''
        Custom analyzers for the language. Will be added in ES index settings.
        '''
        analyzers = {}
        if self.standard_analyzer_name != 'standard':
            analyzers[self.standard_analyzer_name] = self._standard_analyzer()
        if self.has_stopwords:
            analyzers[self.clean_analyzer_name] = self._clean_analyzer()
        if self.has_stemming:
            analyzers[self.stemmed_analyzer_name] = self._stemmed_analyzer()
        return analyzers


    standard_analyzer_name = 'standard'
    '''
    Name of the default text analyzer for the field. This is on the base field and the
    token count multifield.

    In most cases, Elasticsearch's `standard` analyzer is appropriate here, but you
    can use a custom analyzer here if needed. Keep in mind: this analyzer should function
    as the "minimum" level of analysis. It should be transparent and unintrusive
    to users. If you want more "heavy" analysis, you can always add extra multifields.
    '''

    def _standard_analyzer(self) -> Optional[Dict]:
        '''
        Specification for the customised "standard" analyzer for text fields, if any.
        '''
        return None


    def stopwords(self) -> Optional[List[str]]:
        '''
        Fetch list of stopwords for the language
        '''
        if self.has_stopwords:
            return read_nltk_stopwords(get_language_key(self.code))


    @property
    def _stopwords_filter_name(self) -> Optional[str]:
        '''
        Name of the stopwords token filter.
        '''
        if self.has_stopwords:
            return analyzer_name('stopwords', self.code)


    @property
    def clean_analyzer_name(self) -> Optional[str]:
        '''
        Name of the "clean" analyzer (which removes stopwords).
        '''
        if self.has_stopwords:
            return analyzer_name('clean', self.code)


    def _clean_analyzer(self) -> Optional[Dict]:
        '''
        Specification of the "clean" analyzer (which removes stopwords), if supported.

        Will be used in a 'clean' multifield.
        '''
        if self.has_stopwords:
            return {
                'tokenizer': 'standard',
                'char_filter': ['number_filter'],
                'filter': ['lowercase', self._stopwords_filter_name]
            }

    @property
    def _stemmer_filter_name(self) -> Optional[str]:
        '''
        Name of the stemmer token filter, if supported.
        '''
        if self.has_stemming:
            return analyzer_name('stemmer', self.code)

    @property
    def _stemmer_filter_language(self) -> Optional[str]:
        '''
        Value for "language" parameter for the stemmer filter, if supported.

        See https://www.elastic.co/guide/en/elasticsearch/reference/8.17/analysis-stemmer-tokenfilter.html#analysis-stemmer-tokenfilter-language-parm
        '''
        if self.has_stemming:
            return get_language_key(self.code)

    @property
    def stemmed_analyzer_name(self) -> Optional[str]:
        '''
        Name of the "stemmed" analyzer, if supported.
        '''
        if self.has_stemming:
            return analyzer_name('stemmed', self.code)

    def _stemmed_analyzer(self) -> Optional[Dict]:
        '''
        Specification for "stemmed" analyzer, if supported.

        This removes stopwords and stems tokens. Will be used in a 'stemmed' multifield.
        '''
        if self.has_stemming:
            analyzer = self._clean_analyzer()
            analyzer['filter'].append(self._stemmer_filter_name)
            return analyzer


# LANGUAGE SPECS
#========================================================================================

class Chinese(LanguageAnalyzer):
    code = 'zh'
    has_stopwords = True
    has_stemming = False

    standard_analyzer_name = analyzer_name('standard', code)

    def _standard_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': [
                'cjk_width',
                'lowercase',
            ]
        }


class Danish(LanguageAnalyzer):
    code = 'da'
    has_stopwords = True
    has_stemming = True


class Dutch(LanguageAnalyzer):
    code = 'nl'
    has_stopwords = True
    has_stemming = True


class English(LanguageAnalyzer):
    code = 'en'
    has_stopwords = True
    has_stemming = True


class Finnish(LanguageAnalyzer):
    code = 'fi'
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


    def _clean_analyzer(self):
        analyzer = super()._clean_analyzer()
        analyzer['filter'] = [
            'french_elision',
            'lowercase',
            self._stopwords_filter_name,
        ]
        return analyzer


class German(LanguageAnalyzer):
    code = 'de'
    has_stopwords = True
    has_stemming = True

    def _clean_analyzer(self):
        analyzer = super()._clean_analyzer()
        analyzer['filter'] = [
            'lowercase',
            'german_normalization',
            self._stopwords_filter_name,
        ]
        return analyzer


class Norwegian(LanguageAnalyzer):
    code = 'no'
    has_stopwords = True
    has_stemming = True


class Swedish(LanguageAnalyzer):
    code = 'sv'
    has_stopwords = True
    has_stemming = True

# Full language list, and dummy class for unknown language fields

LANGUAGES: List[Type[LanguageAnalyzer]] = [
    Chinese,
    Danish,
    Dutch,
    English,
    Finnish,
    French,
    German,
    Norwegian,
    Swedish,
]

class Unknown(LanguageAnalyzer):
    code = 'und'
    has_stopwords = False
    has_stemming = False


def get_analyzer(language_tag: str) -> LanguageAnalyzer:
    '''
    Get the text analysis configuration for a language.

    Uses `closest_match` so this may return the analyzer for a highly similar language, a
    macrolanguage, etc. Returns the Unknown analyzer if there is no (close) match.
    '''
    supported = { cls.code : cls for cls in LANGUAGES }
    match, _distance = closest_match(
        language_tag,
        list(supported.keys()),
        max_distance=9
    )
    result_options = supported | { 'und': Unknown }
    analyzer_class = result_options[match]
    return analyzer_class()
