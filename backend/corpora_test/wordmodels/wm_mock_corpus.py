import datetime
from addcorpus.python_corpora.corpus import CorpusDefinition, FieldDefinition

from os.path import abspath, dirname, join

here = abspath(dirname(__file__))

class WordmodelsMockCorpus(CorpusDefinition):
    '''
    Corpus with diachronic word models.
    '''

    title = "Word model corpus"
    description = "Mock corpus for testing word models"
    min_date = datetime.datetime(year=1810, month=1, day=1)
    max_date = datetime.datetime(year=1899, month=12, day=31)
    data_directory = None
    word_model_path = join(here, 'mock-word-models')
    wordmodels_page = 'documentation.md'
    fields = [
        FieldDefinition(
            name = 'content',
            display_type='text_content'
        ),
        FieldDefinition(
            name='date',
            display_type='date'
        )
    ]
    languages = ['en']
    category = 'book'

