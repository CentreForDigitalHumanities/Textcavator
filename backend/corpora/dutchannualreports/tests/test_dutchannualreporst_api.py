import os
from corpora.utils_test import corpus_from_api

_here = os.path.abspath(os.path.dirname(__file__))

def test_dutchannualreports(settings, db, admin_client):
    settings.CORPORA = {
        'dutch-annual-reports': 'corpora.dutchannualreports.dutchannualreports.DutchAnnualReports',
    }
    settings.DUTCHANNUALREPORTS_DATA = os.path.join(_here, 'data')

    corpus = corpus_from_api(admin_client, 'dutch-annual-reports')
    assert corpus['title'] == 'Dutch Annual Reports'

