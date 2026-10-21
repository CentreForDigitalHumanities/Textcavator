import os

import pytest

here = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture()
def peace_test_settings(settings):
    settings.CORPORA = {
        'peaceportal': 'corpora.peaceportal.peaceportal.PeacePortal',
        'peaceportal-epidat': 'corpora.peaceportal.epidat.PeaceportalEpidat',
        'peaceportal-fiji': 'corpora.peaceportal.FIJI.fiji.PeaceportalFIJI',
        'peaceportal-iis': 'corpora.peaceportal.iis.PeaceportalIIS',
        'peaceportal-tol': 'corpora.peaceportal.tol.PeaceportalTOL',
    }

    settings.CORPUS_SETTINGS = {
        'peaceportal': {
            'data_directory': os.path.join(here, 'tests', 'data', 'epidat'),
            'es_alias': 'peaceportal'
        },
        'peaceportal-fiji': {
            'data_directory': os.path.join(here, 'tests', 'data', 'fiji')
        },
        'peaceportal-iis': {
            'data_directory': os.path.join(here, 'tests', 'data', 'iis', 'xml'),
            'iis_text_data': os.path.join(here, 'tests', 'data', 'iis', 'transcription_txts')
        },
        'peaceportal-tol': {
            'data_directory': os.path.join(here, 'tests', 'data', 'tol')
        }

    }
