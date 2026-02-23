import pytest
import os
import shutil
from addcorpus import es_settings, language_utils

def test_stopwords(clean_nltk_data_directory, settings, connected_to_internet):
    """
    Check that stopwords results are valid and all languages are included
    """
    settings.NLTK_DATA_PATH = clean_nltk_data_directory
    cases = [
        {
            'language': 'en',
            'stopwords': ['the', 'i', 'have']
        },
        {
            'language': 'nl',
            'stopwords': ['ik']
        },
        {
            'language': 'de',
            'stopwords': ['ich']
        },
        {
            'language': 'fr',
            'stopwords': ['je']
        },
        {
            'language': 'da',
            'stopwords': ['jeg']
        },
        {
            'language': 'no',
            'stopwords': ['jeg']
        },
        {
            'language': 'sv',
            'stopwords': ['jag']
        },
        {
            'language': 'fi',
            'stopwords': ['minä']
        }
    ]

    for case in cases:
        stopwords = language_utils.get_nltk_stopwords(case['language'])
        for word in case['stopwords']:
            assert word in stopwords


@pytest.fixture
def clean_nltk_data_directory(settings):
    """
    Temporarily move already downloaded nltk_data if it was already downloaded,
    and restore the nltk_data directory after testing. If no nltk_data folder existed,
    data downloaded during testing will also be removed when done.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(here, '_nltk_data_temp')
    yield data_path

    shutil.rmtree(data_path)
