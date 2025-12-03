import glob
import os
from typing import List

from ianalyzer_readers.extract import CSV
from ianalyzer_readers.readers.core import Field as ReaderField
from ianalyzer_readers.readers.core import Reader
from ianalyzer_readers.readers.csv import CSVReader

from addcorpus.models import Corpus, Field, CorpusDataFile
from addcorpus.python_corpora.load_corpus import load_corpus_definition
from addcorpus.validation.indexing import validate_has_data


def make_reader_field(corpus_field: Field) -> ReaderField:
    return ReaderField(
        name=corpus_field.name,
        extractor=CSV(corpus_field.extract_column),
    )


def make_reader(corpus: Corpus) -> Reader:
    '''
    From a corpus, returns a Reader object that allows source extraction

    For Python corpora, simply loads the definition class,
    for JSON based corpora, construct Reader from the database.
    '''
    if corpus.has_python_definition:
        return load_corpus_definition(corpus.name)

    validate_has_data(corpus)
    sources_list = _corpus_sources(corpus)

    class NewReader(CSVReader):
        delimiter = corpus.configuration.source_data_delimiter
        fields = [make_reader_field(f)
                  for f in corpus.configuration.fields.all()]

        def sources(self, *args, **kwargs):
            return sources_list

    return NewReader()


def _corpus_sources(corpus: Corpus) -> List[str]:
    if corpus.configuration.data_directory:
        data_directory = corpus.configuration.data_directory
        return glob.glob(f'{data_directory}/**/*.csv', recursive=True)
    else:
        datafiles = CorpusDataFile.objects.filter(corpus=corpus, confirmed=True)
        return [os.path.abspath(df.file.path) for df in datafiles]
