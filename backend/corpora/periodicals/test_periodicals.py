import os
from corpora.utils_test import corpus_from_api

here = os.path.abspath(os.path.dirname(__file__))

def test_periodicals(settings, db, admin_client):
    settings.CORPORA = {
        'periodicals': 'corpora.periodicals.periodicals.Periodicals',
    }
    settings.PERIODICALS_DATA = ''

    corpus = corpus_from_api(admin_client, 'periodicals')
    assert corpus['title'] == 'Periodicals'
