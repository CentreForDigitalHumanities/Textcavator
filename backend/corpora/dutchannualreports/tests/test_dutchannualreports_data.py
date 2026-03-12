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
    assert docs[0] == {
        'company': 'ING',
        'company_type': 'Financial',
        'year': 2008,
        'content': 'ING Group\nAnnual Report\n2008\nSteering the business through turbulent times',
        'image_path': 'newdata/2008/ING 2008.pdf',
        'page': 1,
        'id': 'ING_2008_1',
    }


def test_old_data_reader(settings):
    settings.DUTCHANNUALREPORTS_DATA = os.path.join(_here, 'data')
    reader = DutchAnnualReportsOldDataReader()
    docs = list(reader.documents())
    assert len(docs) == 10
    assert docs[0] == {
        'company': 'Triodos Bank',
        'company_type': 'Financial',
        'year': 1995,
        'content': 'internationaal instituut voor sociale geschiedenis Jaarverslagen Banken *224^ Internationaal Instituut voor Sociale Geschiedenis Cruquiusweg 31 1019 AT Amsterdam Nederland',
        'image_path': 'Financials/TRIODOS_1995_00224/TRIODOS_1995_00224.pdf',
        'file_path': 'Financials/TRIODOS_1995_00224/TRIODOS_1995_00224.xml',
        'page': 1,
        'id': 'TRIODOS_1995_Page1',
    }


def test_dutch_annual_reports(settings, db):
    settings.CORPORA = {
        'dutch-annual-reports': 'corpora.dutchannualreports.dutchannualreports.DutchAnnualReports',
    }
    settings.DUTCHANNUALREPORTS_DATA = os.path.join(_here, 'data')
    corpus = load_corpus_definition('dutch-annual-reports')
    docs = list(corpus.documents())
    assert len(docs) == 30
