from datetime import datetime
import random

from addcorpus.python_corpora.corpus import CorpusDefinition, FieldDefinition
from addcorpus.es_mappings import date_mapping, text_mapping

TOTAL_DOCUMENTS = 11000

# some constants for generating data
MIN_YEAR = 1800
MAX_YEAR = 1900
WORDS = [ 'quick', 'brown', 'fox', 'jumped', 'over', 'lazy', 'dog' ]

def generate_date():
    year = random.randint(MIN_YEAR, MAX_YEAR)
    month = random.randint(1, 12)
    date = datetime(year = year, month = month, day = 1)
    return date.strftime('%Y-%m-%d')

def generate_text():
    tokens = ['the', 'the'] + random.sample(WORDS, 3) # make sure 'the' will have 2 hits per document
    random.shuffle(tokens)
    return ' '.join(tokens)

class LargeMockCorpus(CorpusDefinition):
    '''
    Corpus with a large dataset (> 10.000 documents).

    Documents are small and randomly generated.

    Useful for testing downloads and full data visualisations that need to go past
    10.000 documents.
    '''

    title = 'Large mock Corpus'
    description = 'Corpus for testing'
    visualize = []
    min_date = datetime(year=1800, month=1, day=1)
    max_date = datetime(year=1899, month=12, day=31)
    data_directory = None
    languages = ['en']
    category = 'book'

    def sources(self, start=min_date, end=max_date):
        return range(TOTAL_DOCUMENTS)

    def source2dicts(self, source, **kwargs):
        return [{
            'date': generate_date(),
            'content': generate_text()
        }]

    date = FieldDefinition(
        name = 'date',
        es_mapping = date_mapping()
    )

    content = FieldDefinition(
        name = 'content',
        display_type='text_content',
        es_mapping = text_mapping()
    )

    fields = [date, content]

SPECS = {
    'min_date': LargeMockCorpus.min_date,
    'max_date': LargeMockCorpus.max_date,
    'total_docs': 11000,
    'total_words': 55000,
    'has_token_counts': False,
    'fields': ['date', 'content'],
    'example_query': 'the',
    'content_field': 'content',
}
