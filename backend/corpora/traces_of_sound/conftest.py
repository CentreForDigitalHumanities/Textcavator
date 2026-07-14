from os.path import abspath, dirname, join
import pytest

here = abspath(dirname(__file__))

@pytest.fixture()
def traces_corpora_settings(settings):
    settings.CORPORA = {
        'traces-of-sound': 'corpora.traces_of_sound.traces_of_sound.TracesOfSound',
    }
    settings.CORPUS_SETTINGS['traces-of-sound'] = {
        'data_directory': join(here, 'tests', 'data')
    }
