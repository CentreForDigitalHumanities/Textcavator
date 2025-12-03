from enum import Enum

CATEGORIES = [
    ('parliament', 'Parliamentary debates'),
    ('periodical', 'Newspapers and other periodicals'),
    ('finance', 'Financial reports'),
    ('ruling', 'Laws and rulings'),
    ('review', 'Reviews and discussions'),
    ('inscription', 'Funerary inscriptions'),
    ('oration', 'Orations'),
    ('book', 'Books'),
    ('letter', 'Letters and life writing'),
    ('poetry', 'Poetry and songs'),
    ('social', 'Social media'),
    ('other', 'Other'),
]
'''
Types of data
'''

class MappingType(Enum):
    'Elasticsearch mapping types that are implemented in Textcavator'

    TEXT = 'text'
    KEYWORD = 'keyword'
    DATE = 'date'
    DATE_RANGE = 'date_range'
    INTEGER  = 'integer'
    FLOAT = 'float'
    BOOLEAN = 'boolean'
    GEO_POINT = 'geo_point'


class VisualizationType(Enum):
    '''Types of visualisations available'''

    RESULTS_COUNT = 'resultscount'
    TERM_FREQUENCY = 'termfrequency'
    NGRAM = 'ngram'
    WORDCLOUD = 'wordcloud'
    MAP = 'map'

FORBIDDEN_FIELD_NAMES = [
    'query',
    'fields',
    'sort',
    'highlight',
    'visualize',
    'visualizedField',
    'normalize',
    'ngramSettings',
    'p',
    'tags',
    'tab',
    'document_link',
]
'''
Field names that cannot be used because they interfere with other functionality.

This is usually because they are also query parameters in frontend routes, and using them
would make routing ambiguous.

`query` and `document_link` are forbidden because they are reserved columns in CSV downloads.

'''
