import os
from corpora.utils_test import corpus_from_api

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

def test_emblems_import(settings, db, admin_client):
    settings.CORPORA = {
        'emblems': 'corpora.emblems.emblems.Emblems',
    }
    settings.CORPUS_SETTINGS = {
        'emblems': {
            'data_directory': DATA_DIR,
            'es_index': 'test-emblems',
        }
    }

    corpus_from_api(admin_client, 'emblems')
