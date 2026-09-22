import os

from textcavator_readers.readers.csv import CSVReader
from textcavator_readers.readers.xml import XMLReader
from textcavator_readers.extract import CSV, XML, Metadata
from textcavator_readers.readers.core import Field

# TODO: make test data
DATA_DIR = '../../corpora/emblems/'

class EmblemsIndexReader(CSVReader):
    data_directory = None
    required_field = 'Author'

    def __init__(self, data_directory):
        self.data_directory = data_directory

    def sources(self, **kwargs):
        return [
            os.path.join(self.data_directory, 'index.csv')
        ]

    fields = [
        Field(
            name='author',
            extractor=CSV('Author'),
        ),
        Field(
            name='title',
            extractor=CSV('Title'),
        ),
        Field(
            name='year',
            extractor=CSV('year', transform=int),
        ),
        Field(
            name='id',
            extractor=CSV('ID'),
        ),
    ]


class EmblemsDataReader(XMLReader):
    data_directory = DATA_DIR

    def sources(self, **kwargs):
        index_reader = EmblemsIndexReader(self.data_directory)
        for doc in index_reader.documents():
            filename = doc['id'] + '.xml'
            path = os.path.join(self.data_directory, 'xml', filename)
            yield path, doc

    fields = [
        Field(
            name='author',
            extractor=Metadata('author'),
        ),
        Field(
            name='title',
            extractor=Metadata('title'),
        ),
        Field(
            name='year',
            extractor=Metadata('year'),
        )
    ]

