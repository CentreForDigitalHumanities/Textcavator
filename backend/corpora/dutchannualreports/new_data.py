import os

from ianalyzer_readers.readers.csv import CSVReader
from ianalyzer_readers.extract import CSV, Metadata
from ianalyzer_readers.readers.core import Field
from django.conf import settings

from corpora.dutchannualreports.pdf_reader import PDFReader, PageText

class NewDataIndexReader(CSVReader):
    @property
    def data_directory(self):
        return os.path.join(settings.DUTCHANNUALREPORTS_DATA, 'newdata')

    def sources(self, **kwargs):
        path = os.path.join(self.data_directory, 'metadata.csv')
        yield path

    fields = [
        Field(
            name='path',
            extractor=CSV('path'),
        ),
        Field(
            name='year',
            extractor=CSV('year', transform=int),
        ),
        Field(
            name='company',
            extractor=CSV('company'),
        )
    ]

class NewDataReader(PDFReader):
    def __init__(self, **kwargs):
        self.index_reader = NewDataIndexReader(**kwargs)

    @property
    def data_directory(self):
        return self.index_reader.data_directory

    def sources(self, **kwargs):
        docs = self.index_reader.documents(**kwargs)
        for doc in docs:
            path = os.path.join(self.data_directory, doc['path'])
            yield path, doc

    fields = [
        Field(
            name='content',
            extractor=PageText()
        ),
        Field(
            name='company',
            extractor=Metadata('company')
        ),
        Field(
            name='year',
            extractor=Metadata('year')
        )
    ]
