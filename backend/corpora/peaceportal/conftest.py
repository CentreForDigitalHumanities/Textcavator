import pytest
import os

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

    settings.PEACEPORTAL_EPIDAT_DATA= os.path.join(here, 'tests', 'data', 'epidat')
    settings.PEACEPORTAL_FIJI_DATA= os.path.join(here, 'tests', 'data', 'fiji')
    settings.PEACEPORTAL_IIS_DATA = os.path.join(here, 'tests', 'data', 'iis', 'xml')
    settings.PEACEPORTAL_IIS_TXT_DATA = os.path.join(here, 'tests', 'data', 'iis', 'transcription_txts')
    settings.PEACEPORTAL_TOL_DATA = os.path.join(here, 'tests', 'data', 'tol')
    settings.PEACEPORTAL_ALIAS = 'peaceportal'
