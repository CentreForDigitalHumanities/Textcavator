from datetime import datetime
import os

from ianalyzer_readers.extract import CSV

from addcorpus.python_corpora.corpus import CSVCorpusDefinition, FieldDefinition
from addcorpus.es_mappings import keyword_mapping, int_mapping, main_content_mapping
from addcorpus.es_settings import es_settings

here = os.path.abspath(os.path.dirname(__file__))

class CJKMockCorpus(CSVCorpusDefinition):
    '''
    Corpus with Chinese text to test CJK language analysis & display.
    '''

    title = 'CJK Mock Corpus'
    description = 'Excerpts from Confucius'
    min_date = datetime(year=1800, month=1, day=1)
    max_date = datetime(year=1899, month=12, day=31)
    data_directory = os.path.join(here, 'source_data')
    languages = ['zho']
    category = 'book'

    es_settings = es_settings(['zho'])

    def sources(self, *args, **kwargs):
        yield os.path.join(self.data_directory, 'data.csv')

    fields = [
        FieldDefinition(
            name='chapter',
            es_mapping=keyword_mapping(enable_full_text_search=True),
            extractor=CSV('chapter'),
            language='zho',
        ),
        FieldDefinition(
            name='index',
            es_mapping=int_mapping(),
            extractor=CSV('index'),
        ),
        FieldDefinition(
            name='character',
            es_mapping=keyword_mapping(enable_full_text_search=True),
            extractor=CSV('character'),
            language='zho',
        ),
        FieldDefinition(
            name='content',
            display_type='text_content',
            es_mapping=main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                language='zho'
            ),
            language='zho',
            extractor=CSV('content'),
        )
    ]
