import os
import re

from ianalyzer_readers.readers.csv import CSVReader
from ianalyzer_readers.extract import CSV, Metadata, Order, Combined
from ianalyzer_readers.readers.core import Field
from django.conf import settings

from corpora.dutchannualreports.pdf_reader import PDFReader, PageText

class NewDataIndexReader(CSVReader):
    @property
    def data_directory(self):
        return settings.DUTCHANNUALREPORTS_DATA

    def sources(self, **kwargs):
        path = os.path.join(self.data_directory, 'newdata', 'metadata.csv')
        yield path

    def _abs_path(self, path: str) -> str:
        '''Transform path within newdata subdirectory to absolute path'''
        return os.path.join(self.data_directory, 'newdata', path)

    def _rel_path(self, path: str) -> str:
        '''Transform path within newdata subdirectory to one relative to the corpus data
        directory.'''
        abs_path = self._abs_path(path)
        return os.path.relpath(abs_path, self.data_directory)

    @property
    def fields(self):
        return [
            Field(
                name='abs_path',
                extractor=CSV('path', transform=self._abs_path),
            ),
            Field(
                name='rel_path',
                extractor=CSV('path', transform=self._rel_path)
            ),
            Field(
                name='year',
                extractor=CSV('year', transform=int),
            ),
            Field(
                name='company',
                extractor=CSV('company'),
            ),
            Field(
                name='company_type',
                extractor=CSV('sector')
            ),
        ]

def format_company_id(name: str) -> str:
    return re.sub('\W+', '_', name).upper()

class NewDataReader(PDFReader):
    def __init__(self, **kwargs):
        self.index_reader = NewDataIndexReader(**kwargs)


    def sources(self, **kwargs):
        docs = self.index_reader.documents(**kwargs)
        for doc in docs:
            yield doc['abs_path'], doc

    fields = [
        Field(
            name='content',
            extractor=PageText()
        ),
        Field(
            name='image_path',
            extractor=Metadata('rel_path'),
        ),
        Field(
            name='page',
            extractor=Order(transform=lambda i: i + 1)
        ),
        Field(
            name='company',
            extractor=Metadata('company')
        ),
        Field(
            name='company_type',
            extractor=Metadata('company_type')
        ),
        Field(
            name='year',
            extractor=Metadata('year')
        ),
        Field(
            name='id',
            extractor=Combined(
                Metadata('company', transform=format_company_id),
                Metadata('year', transform=str),
                Order(transform=lambda i: str(i + 1)),
                transform='_'.join,
            )
        )
    ]
