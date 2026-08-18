import pytest
from addcorpus.language_analyzers import get_analyzer

def test_stopwords(tmp_nltk_data_directory):
    """
    Check that stopwords results are valid and all languages are included
    """
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
        analyzer = get_analyzer(case['language'])
        stopwords = analyzer.stopwords()
        for word in case['stopwords']:
            assert word in stopwords
