from typing import List

from addcorpus.language_analyzer_base import LanguageAnalyzer
from addcorpus.es_settings import es_settings

class CustomEmblemsAnalyzer(LanguageAnalyzer):
    'Custom analyzer for original text. Adds ASCII folding (i.e. ignores accents)'

    code = 'unk' # = unknown
    has_stopwords = False
    has_stemming = False
    standard_analyzer_name = 'standard_unk'

    def _standard_analyzer(self):
        return {
            'tokenizer': 'standard',
            'filter': ['asciifolding', 'lowercase'],
            'char_filter': [
                # replace ligatures
                {
                    'type': 'mapping',
                    'mappings': [
                        'æ => ae',
                        'œ => oe',
                        'Æ => AE',
                        'Œ => OE',
                    ],
                }
            ]
        }


def es_settings_with_custom_analyzers(languages: List[str], custom: List[LanguageAnalyzer]):
    settings = es_settings(languages)
    for analyzer in custom:
        settings['analysis']['char_filter'] |= analyzer.char_filters()
        settings['analysis']['filter'] |= analyzer.token_filters()
        settings['analysis']['analyzer'] |= analyzer.analyzers()
    return settings
