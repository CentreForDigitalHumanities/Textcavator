import os
from corpora.utils_test import corpus_from_api

here = os.path.abspath(os.path.dirname(__file__))

def test_goodreads(settings, db, admin_client):
    settings.CORPORA = {
        'goodreads': 'corpora.goodreads.goodreads.GoodReads'
    }
    settings.CORPUS_SETTINGS = {
        'goodreads': {
            'data_directory': ''
        }
    }

    corpus = corpus_from_api(admin_client, 'goodreads')
    assert corpus['title'] == 'DIOPTRA-L'
