import os
from corpora.utils_test import corpus_from_api

here = os.path.abspath(os.path.dirname(__file__))

def test_dutchnewspapers_public(settings, db, admin_client):
    settings.CORPORA = {
        'dutchnewspapers-public': os.path.join(here, 'dutchnewspapers_public.py')
    }
    settings.DUTCHNEWSPAPERS_DATA = ''

    corpus = corpus_from_api(admin_client, 'dutchnewspapers-public')
    assert corpus['title'] == 'Dutch Newspapers (public)'

def test_dutchnewspapers_all(settings, admin_client):
    settings.CORPORA = {
        'dutchnewspapers-all': os.path.join(here, 'dutchnewspapers_all.py'),
        'dutchnewspapers-public': os.path.join(here, 'dutchnewspapers_public.py')
    }
    settings.DUTCHNEWSPAPERS_DATA = ''
    settings.DUTCHNEWSPAPERS_ALL_DATA = ''

    corpus = corpus_from_api(admin_client, 'dutchnewspapers-all')
    assert corpus['title'] == 'Dutch Newspapers (full)'
