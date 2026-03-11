import os
from addcorpus.python_corpora.save_corpus import load_corpus_definition

from corpora.dutchannualreports.new_data import NewDataReader
from corpora.dutchannualreports.old_data import DutchAnnualReportsOldDataReader

_here = os.path.abspath(os.path.dirname(__file__))


def test_new_data_reader(settings):
    settings.DUTCHANNUALREPORTS_DATA = os.path.join(_here, 'data')
    reader = NewDataReader()
    docs = list(reader.documents())
    assert len(docs) == 20


def test_new_data_reader(settings):
    settings.DUTCHANNUALREPORTS_DATA = os.path.join(_here, 'data')
    reader = DutchAnnualReportsOldDataReader()
    docs = list(reader.documents())
    assert len(docs) == 10


def test_dutch_annual_reports(settings, db):
    settings.CORPORA = {
        'dutch-annual-reports': 'corpora.dutchannualreports.dutchannualreports.DutchAnnualReports',
    }
    settings.DUTCHANNUALREPORTS_DATA = os.path.join(_here, 'data')
    corpus = load_corpus_definition('dutch-annual-reports')
    docs = list(corpus.documents())
    assert len(docs) == 30
