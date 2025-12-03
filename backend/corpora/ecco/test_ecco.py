import os
from corpora.utils_test import corpus_from_api

here = os.path.abspath(os.path.dirname(__file__))

def test_ecco(settings, db, admin_client):
    settings.CORPORA = {
        'ecco': os.path.join(here, 'ecco.py')
    }
    settings.ECCO_DATA = ''

    corpus = corpus_from_api(admin_client, 'ecco')
    assert corpus['title'] == 'Eighteenth Century Collections Online'
