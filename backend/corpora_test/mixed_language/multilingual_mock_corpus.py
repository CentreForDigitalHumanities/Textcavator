from datetime import datetime
import os

from ianalyzer_readers.extract import CSV

from addcorpus.python_corpora.corpus import FieldDefinition, CSVCorpusDefinition
from addcorpus.es_mappings import keyword_mapping, text_mapping

# Fake corpus class for unit tests

here = os.path.abspath(os.path.dirname(__file__))

class MultilingualMockCorpus(CSVCorpusDefinition):
    '''
    Corpus that includes multiple languages.

    The source data of this corpus includes diacritics, so this corpus is useful
    for testing encoding.
    '''

    title = 'Multilingual Mock Corpus'
    description = 'A mixed-language corpus.'
    visualize = []
    min_date = datetime(year=2000, month=1, day=1)
    max_date = datetime(year=2022, month=12, day=31)
    data_directory = os.path.join(here, 'source_data')
    languages = ['sv', 'de']
    category = 'book'

    def sources(self, *args, **kwargs):
        for csv_file in os.listdir(self.data_directory):
            yield os.path.join(self.data_directory, csv_file), {}


    content = FieldDefinition(
        name = 'content',
        display_type='text_content',
        es_mapping = text_mapping(),
        extractor = CSV('content')
    )

    language = FieldDefinition(
        name = 'language',
        es_mapping = keyword_mapping(),
        extractor = CSV('language'),
        searchable=False,
    )

    fields = [content, language]

SPECS = {
    'min_date': MultilingualMockCorpus.min_date,
    'max_date': MultilingualMockCorpus.max_date,
    'total_docs': 2,
    'total_words': 176,
    'has_token_counts': False,
    'fields': ['content', 'language'],
    'example_query': 'sprache',
    'content_field': 'content',
}
