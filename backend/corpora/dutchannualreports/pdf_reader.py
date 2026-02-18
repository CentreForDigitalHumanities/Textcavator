# TODO: delete this an import from ianalyzer_readers
'''
Defines a `PDFReader` which is intended to extract text data from PDFs.
'''

from pypdf import PdfReader as PyPdfReader
from pypdf import PageObject
from typing import Dict
from ianalyzer_readers.readers.core import Reader
from ianalyzer_readers.extract import Extractor

class PDFReader(Reader):
    '''
    Base class for PDF text extraction. Thin wrapper for `pypdf`.

    Can be paired with the `PageText` extractor to get the text per page.
    '''

    def data_from_file(self, path: str) -> PyPdfReader:
        return PyPdfReader(path)

    def iterate_data(self, data: PyPdfReader, metadata):
        for page in data.pages:
            yield {'page': page}


class PageText(Extractor):
    '''
    Extracts text from a PDF page object.

    See https://pypdf.readthedocs.io/en/stable/user/extract-text.html

    Parameters:
        options: these are passed on to `extract_text` (documentation linked above).
    '''

    def __init__(self, options: Dict = dict(), **kwargs):
        self.options = options
        super().__init__(**kwargs)

    def _apply(self, page: PageObject, **kwargs):
        return page.extract_text(**self.options)
