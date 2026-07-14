import os
from corpora.utils_test import corpus_from_api

here = os.path.abspath(os.path.dirname(__file__))

def test_goodreads(settings, db, admin_client):
    settings.CORPORA = {
        'goodreads': 'corpora.goodreads.goodreads.GoodReads'
    }
    settings.GOODREADS_DATA = ''

    corpus = corpus_from_api(admin_client, 'goodreads')
    assert corpus['title'] == 'DIOPTRA-L'
