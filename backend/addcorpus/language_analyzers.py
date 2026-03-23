'''
Analyzer specifications per language.

In most cases, you should NOT import the analyzer classes directly. Use the
`get_analyzer` function in this module to select the language from the IETF tag.
'''

from typing import List, Type

from langcodes import closest_match

from addcorpus.language_utils import analyzer_name, read_stopwords
from addcorpus.language_analyzer_base import LanguageAnalyzer


# To add a new language, add the class below and list it in LANGUAGES.
# Classes are listed alphabetically.

# It is worth looking at the built-in language analyzers from Elasticsearch:
# https://www.elastic.co/guide/en/elasticsearch/reference/8.17/analysis-lang-analyzer.html
# These may include language-specific filters that can be useful.


class Basque(LanguageAnalyzer):
    code = 'eu'
    has_stopwords = True
    has_stemming = True


class Bosnian(LanguageAnalyzer):
    code = 'bs'
    has_stopwords = True
    has_stemming = False

    _stopwords_source = 'supplementary'


class Bulgarian(LanguageAnalyzer):
    code = 'bg'
    has_stopwords = True
    has_stemming = True

    _stopwords_source = 'supplementary'


class Catalan(LanguageAnalyzer):
    code = 'ca'
    has_stopwords = True
    has_stemming = True

    def token_filters(self):
        filters = super().token_filters()
        filters['catalan_elision'] = {
            'type': 'elision',
            'articles': ['d', 'l', 'm', 'n', 's', 't'],
            'articles_case': True,
        }
        return filters

    def _clean_analyzer(self):
        analyzer = super()._clean_analyzer()
        analyzer['filter'] = [
            'catalan_elision', 'lowercase', self._stopwords_filter_name,
        ]
        return analyzer


class Croatian(LanguageAnalyzer):
    code = 'hr'
    has_stopwords = True
    has_stemming = False

    _stopwords_source = 'supplementary'


class Czech(LanguageAnalyzer):
    code = 'cs'
    has_stopwords = True
    has_stemming = True

    _stopwords_source = 'supplementary'


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

    def token_filters(self):
        filters = super().token_filters()
        filters['stemmer_possessive_en'] = {
            'type': 'stemmer',
            'language': 'possessive_english'
        }
        return filters

    standard_analyzer_name = 'standard_en'

    def _standard_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': ['stemmer_possessive_en', 'lowercase']
        }

    def _clean_analyzer(self):
        analyzer = super()._clean_analyzer()
        analyzer['filter'] = [
            'stemmer_possessive_en', 'lowercase', self._stopwords_filter_name
        ]
        return analyzer


class Estonian(LanguageAnalyzer):
    code = 'et'
    has_stopwords = True
    has_stemming = True

    _stopwords_source = 'supplementary'


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
        }
        return filters

    def _clean_analyzer(self):
        analyzer = super()._clean_analyzer()
        analyzer['filter'] = [
            'french_elision',
            'lowercase',
            self._stopwords_filter_name,
        ]
        return analyzer

    _stemmer_filter_language = 'light_french'


class Galician(LanguageAnalyzer):
    code = 'gl'
    has_stopwords = True
    has_stemming = True

    _stopwords_source = 'supplementary'


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

    _stemmer_filter_language = 'light_german'


class Greek(LanguageAnalyzer):
    code = 'el'
    has_stopwords = True
    has_stemming = True

    def token_filters(self):
        filters = super().token_filters()
        filters['lowercase_el'] = self._lowercase_filter()
        return filters

    def _lowercase_filter(self):
        return {'type': 'lowercase', 'language': 'greek'}

    standard_analyzer_name = analyzer_name('standard', code)

    def _standard_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': ['lowercase_el']
        }

    def _clean_analyzer(self):
        analyzer = super()._clean_analyzer()
        analyzer['filter'] = ['lowercase_el', self._stopwords_filter_name]
        return analyzer


class Hebrew(LanguageAnalyzer):
    code = 'he'
    has_stopwords = True
    has_stemming = False


class Icelandic(LanguageAnalyzer):
    code = 'is'
    has_stopwords = True
    has_stemming = False

    _stopwords_source = 'supplementary'


class Irish(LanguageAnalyzer):
    code = 'ga'
    has_stopwords = True
    has_stemming = True


    def token_filters(self):
        filters = super().token_filters()
        filters.update({
            'hyphenation_ga': {
                'type': 'stop',
                'stopwords': ['h', 'n', 't'],
                'ignore_case': True,
            },
            'elision_ga': {
                'type': 'elision',
                'articles': ['d', 'm', 'b'],
                'articles_case': True,
            },
            'lowercase_ga': {
                'type': 'lowercase',
                'language': 'irish',
            }
        })
        return filters

    standard_analyzer_name = 'standard_ga'

    def _standard_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': ['lowercase_ga']
        }

    _stopwords_source = 'supplementary'

    def _clean_analyzer(self):
        analyzer = super()._clean_analyzer()
        analyzer['filter'] = [
            'hyphenation_ga',
            'elision_ga',
            'lowercase_ga',
            self._stopwords_filter_name
        ]
        return analyzer


class Italian(LanguageAnalyzer):
    code = 'it'
    has_stopwords = True
    has_stemming = True

    def token_filters(self):
        filters = super().token_filters()
        filters['italian_elision'] = {
            'type': 'elision',
            'articles': [
                'c', 'l', 'all', 'dall', 'dell', 'nell', 'sull', 'coll', 'pell', 'gl',
                'agl', 'dagl', 'degl', 'negl', 'sugl', 'un', 'm', 't', 's', 'v', 'd',
            ],
            'articles_case': True,
        }
        return filters

    def _clean_analyzer(self):
        analyzer = super()._clean_analyzer()
        analyzer['filter'] = [
            'italian_elision', 'lowercase', self._stopwords_filter_name
        ]
        return analyzer

    _stemmer_filter_language = 'light_italian'


class Latvian(LanguageAnalyzer):
    code = 'lv'
    has_stopwords = True
    has_stemming = True

    _stopwords_source = 'supplementary'


class MandarinChinese(LanguageAnalyzer):
    code = 'cmn'
    has_stopwords = True
    has_stemming = False

    def stopwords(self):
        return read_stopwords('chinese', 'nltk')

    standard_analyzer_name = analyzer_name('standard', code)

    def char_filters(self):
        return {}

    def _standard_analyzer(self):
        return {
            'tokenizer': 'standard',
            'char_filter': [],
            'filter': [
                'cjk_width',
                'lowercase',
            ],
        }

    def _clean_analyzer(self):
        return {
            'tokenizer': 'standard',
            'char_filter': [],
            'filter': [
                'cjk_width',
                'lowercase',
                self._stopwords_filter_name
            ],
        }


class NorwegianBokmal(LanguageAnalyzer):
    code = 'nb'
    has_stopwords = True
    has_stemming = True

    def stopwords(self):
        return read_stopwords('norwegian', 'nltk')

    _stemmer_filter_language = 'norwegian'


class NorwegianNynorsk(LanguageAnalyzer):
    code = 'nn'
    has_stopwords = True
    has_stemming = True

    def stopwords(self):
        return read_stopwords('norwegian', 'nltk')

    _stemmer_filter_language = 'light_nynorsk'


class Portuguese(LanguageAnalyzer):
    code = 'pt'
    has_stopwords = True
    has_stemming = True

    _stemmer_filter_language = 'light_portuguese'


class Serbian(LanguageAnalyzer):
    code = 'sr'
    has_stopwords = True
    has_stemming = True

    _stopwords_source = 'supplementary'


    def _clean_analyzer(self):
        analyzer = super()._clean_analyzer()
        analyzer['filter'].append('serbian_normalization')
        return analyzer


class Slovenian(LanguageAnalyzer):
    code = 'sl'
    has_stopwords = True
    has_stemming = False

    _stopwords_source = 'supplementary'


class Spanish(LanguageAnalyzer):
    code = 'es'
    has_stopwords = True
    has_stemming = True

    _stemmer_filter_language = 'light_spanish'


class Swedish(LanguageAnalyzer):
    code = 'sv'
    has_stopwords = True
    has_stemming = True


class Turkish(LanguageAnalyzer):
    code = 'tr'
    has_stopwords = True
    has_stemming = True

    def token_filters(self):
        filters = super().token_filters()
        filters['lowercase_tr'] = self._lowercase_filter()
        return filters

    standard_analyzer_name = analyzer_name('standard', code)

    def _lowercase_filter(self):
        return {'type': 'lowercase', 'language': 'turkish'}

    def _standard_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': ['lowercase_tr']
        }

    def _clean_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': ['lowercase_tr', self._stopwords_filter_name]
        }

    def _stemmed_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': [
                'apostrophe',
                'lowercase_tr',
                self._stopwords_filter_name,
                self._stemmer_filter_name,
            ],
        }


class Ukranian(LanguageAnalyzer):
    code = 'uk'
    has_stopwords = True
    has_stemming = True

    _stopwords_source = 'supplementary'


# Full language list, and dummy class for unknown language fields

LANGUAGES: List[Type[LanguageAnalyzer]] = [
    Basque,
    Bosnian,
    Bulgarian,
    Catalan,
    Croatian,
    Czech,
    Danish,
    Dutch,
    English,
    Estonian,
    Finnish,
    French,
    Galician,
    German,
    Greek,
    Hebrew,
    Icelandic,
    Irish,
    Italian,
    Latvian,
    MandarinChinese,
    NorwegianBokmal,
    NorwegianNynorsk,
    Portuguese,
    Serbian,
    Spanish,
    Swedish,
    Slovenian,
    Turkish,
    Ukranian,
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
    if not language_tag:
        return Unknown()

    supported = { cls.code : cls for cls in LANGUAGES }
    match, _distance = closest_match(
        language_tag,
        list(supported.keys()),
        max_distance=9
    )
    result_options = supported | { 'und': Unknown }
    analyzer_class = result_options[match]
    return analyzer_class()
