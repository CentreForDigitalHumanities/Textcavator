import pytest
import os
import shutil
from addcorpus import language_analysis

def test_stopwords(clean_nltk_data_directory, settings):
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
        analyzer = language_analysis.get_analyzer(case['language'])
        stopwords = analyzer.stopwords()
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
