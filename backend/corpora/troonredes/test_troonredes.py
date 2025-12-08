import os
from corpora.utils_test import corpus_from_api

here = os.path.abspath(os.path.dirname(__file__))

def test_troonredes(settings, db, admin_client):
    settings.CORPORA = {
        'troonredes': os.path.join(here, 'troonredes.py')
    }
    settings.TROONREDES_DATA = ''

    corpus = corpus_from_api(admin_client, 'troonredes')
    assert corpus['title'] == 'Troonredes'
