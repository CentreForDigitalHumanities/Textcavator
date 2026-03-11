import os
import pytest
from rest_framework import status

from corpora.utils_test import corpus_from_api
from addcorpus.python_corpora.save_corpus import load_and_save_single_corpus
from addcorpus.python_corpora.save_corpus import load_corpus_definition

_here = os.path.abspath(os.path.dirname(__file__))

NAME = 'dutch-annual-reports'

@pytest.fixture
def corpus_settings(settings):
    settings.CORPORA = {
        NAME: 'corpora.dutchannualreports.dutchannualreports.DutchAnnualReports',
    }
    settings.DUTCHANNUALREPORTS_DATA = os.path.join(_here, 'data')

def test_dutchannualreports(corpus_settings, db, admin_client):
    corpus = corpus_from_api(admin_client, NAME)
    assert corpus['title'] == 'Dutch Annual Reports'

def test_dutchannualreports_media(corpus_settings, db, admin_client):
    load_and_save_single_corpus(NAME)

    reader = load_corpus_definition(NAME)
    for doc in reader.documents():
        document = {'fieldValues': doc}

        response = admin_client.post(
            '/api/request_media',
            {'corpus': NAME, 'document': document},
            content_type='application/json'
        )
        assert status.is_success(response.status_code)
        url = response.data['media'][0]

        response = admin_client.get(url)
        assert status.is_success(response.status_code)

