import os
from corpora.utils_test import corpus_from_api

here = os.path.abspath(os.path.dirname(__file__))

def test_guardian_observer(settings, db, admin_client):
    settings.CORPORA = {
        'guardian-observer': os.path.join(here, 'guardianobserver.py')
    }
    settings.GO_DATA = ''

    corpus = corpus_from_api(admin_client, 'guardian-observer')
    assert corpus['title'] == 'Guardian-Observer'
