from typing import Dict, Iterable
import operator
from functools import reduce

from addcorpus.language_analysis import get_analyzer

def es_settings(languages=[]):
    '''
    Make elasticsearch settings json for a corpus index. Options:
    - `languages`: array of language codes (IETF tags)
    '''
    analyzers = [get_analyzer(lang) for lang in languages]
    analysis = {
        'char_filter': _join_dicts(analyzer.char_filters() for analyzer in analyzers),
        'filter': _join_dicts(analyzer.token_filters() for analyzer in analyzers),
        'analyzer': _join_dicts(analyzer.analyzers() for analyzer in analyzers),
    }

    settings = {
        'index': {'number_of_shards': 1, 'number_of_replicas': 1},
        'analysis': analysis,
    }

    return settings

def _join_dicts(dicts: Iterable[Dict]) -> Dict:
    return reduce(operator.or_, dicts)
