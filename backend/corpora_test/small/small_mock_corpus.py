from datetime import datetime
import os

from addcorpus.python_corpora.corpus import FieldDefinition, CSVCorpusDefinition
from ianalyzer_readers.extract import CSV
from addcorpus.es_mappings import date_mapping, keyword_mapping, main_content_mapping, text_mapping
from addcorpus.es_settings import es_settings


# Fake corpus class for unit tests

here = os.path.abspath(os.path.dirname(__file__))

class SmallMockCorpus(CSVCorpusDefinition):
    '''
    CSV corpus with a small dataset to test queries and aggregations.

    Has multiple field types but a small number of documents, so you can test
    complex queries and visualisations.
    '''

    title = 'Mock Corpus'
    description = 'Corpus for testing'
    visualize = []
    min_date = datetime(year=1800, month=1, day=1)
    max_date = datetime(year=1899, month=12, day=31)
    data_directory = os.path.join(here, 'source_data')
    languages = ['en']
    category = 'book'

    es_settings = es_settings(['en'], stopword_analysis=True)

    def sources(self, *args, **kwargs):
        for csv_file in os.listdir(self.data_directory):
            yield os.path.join(self.data_directory, csv_file), {}

    date = FieldDefinition(
        name = 'date',
        es_mapping = date_mapping(),
        extractor = CSV('date')
    )

    title_field = FieldDefinition(
        name = 'title',
        es_mapping = text_mapping(),
        extractor = CSV('title')
    )

    content = FieldDefinition(
        name = 'content',
        display_type='text_content',
        es_mapping = main_content_mapping(True, True, False, 'en'),
        extractor = CSV('content'),
        language='en',
    )

    genre = FieldDefinition(
        name = 'genre',
        es_mapping = keyword_mapping(),
        extractor = CSV('genre'),
        searchable=False,
    )

    fields = [date, title_field, content, genre]

SPECS = {
    'min_date': SmallMockCorpus.min_date,
    'max_date': SmallMockCorpus.max_date,
    'total_docs': 3,
    'total_words': 67,
    'has_token_counts': True,
    'fields':  ['date', 'title', 'genre', 'content'],
    'example_query': 'to',
    'content_field': 'content',
}
'''
Specifications to test search results in this corpus.
'''
