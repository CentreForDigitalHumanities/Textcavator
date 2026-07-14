import os

import pytest
from requests import Response
from unittest.mock import Mock

here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture()
def gallica_corpus_settings(settings):
    settings.CORPORA = {
        "caricature": 'corpora.gallica.caricature.Caricature',
        "figaro": 'corpora.gallica.figaro.Figaro',
        "journauxresistance": 'corpora.gallica.resistance.JournauxResistance',
    }


def mock_content(filename):
    with open(filename, "r") as f:
        return f.read()


class MockResponseFactory(object):
    def __init__(self, corpus_name: str):
        self.filepath = os.path.join(here, "tests", "data", corpus_name)

    def mock_response(self, url: str) -> Mock:
        if url.endswith("date"):
            filename = os.path.join(self.filepath, "Years.xml")
        elif "&" in url:
            filename = os.path.join(self.filepath, "Issues.xml")
        elif "?" in url:
            filename = os.path.join(self.filepath, "OAIRecord.xml")
        elif url.endswith("texteBrut"):
            filename = os.path.join(self.filepath, "RoughText.html")
        mock = Mock(spec=Response)
        mock.status_code = 200
        mock.content = mock_content(filename)
        return mock


def mock_sleep(seconds: int):
    pass
