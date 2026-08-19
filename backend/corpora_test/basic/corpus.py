from addcorpus.python_corpora.corpus import CSVCorpusDefinition, FieldDefinition
from textcavator_readers.extract import CSV
from addcorpus.es_mappings import keyword_mapping, main_content_mapping
from addcorpus.python_corpora.filters import MultipleChoiceFilter
import os
import datetime

here = os.path.abspath(os.path.dirname(__file__))

class ExampleCorpus(CSVCorpusDefinition):
    '''
    Basic CSV corpus.

    Includes:
    - a tiny CSV dataset to test source extraction.
    - documentation pages

    Also suitable as a base class to test more specific settings.
    '''

    title = "Example"
    description = "Example corpus"
    es_index = 'test-basic-corpus'
    min_date = datetime.datetime(year=1, month=1, day=1)
    max_date = datetime.datetime(year=2022, month=12, day=31)
    data_directory = os.path.join(here, 'source_data')
    citation_page = 'citation.md'
    license_page = 'license.md'
    description_page = 'mock-csv-corpus.md'

    languages = ['en']
    category = 'book'

    def sources(self, *args, **kwargs):
        for filename in os.listdir(self.data_directory):
            if filename.endswith('.csv'):
                full_path = os.path.join(self.data_directory, filename)
                yield full_path, {
                        'filename': filename
                    }

    fields = [
        FieldDefinition(
            name='character',
            display_name='Character',
            description='Character speaking the line',
            extractor = CSV('character'),
            es_mapping=keyword_mapping(),
            search_filter=MultipleChoiceFilter(),
            results_overview=True,
            visualizations=['resultscount', 'termfrequency'],
        ),
        FieldDefinition(
            name = 'line',
            display_type = 'text_content',
            extractor = CSV('line'),
            es_mapping=main_content_mapping(),
            results_overview=True,
            visualizations=['wordcloud'],
        )
    ]
