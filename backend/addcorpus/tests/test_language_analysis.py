import pytest
from addcorpus.language_analysis import get_analyzer, LANGUAGES

def test_get_analyzer():
    assert get_analyzer('nl').code == 'nl'
    assert get_analyzer('nld').code == 'nl'
    assert get_analyzer('nl-BE').code == 'nl'
    assert get_analyzer('nl-Cyrl').code == 'und' # no ignoring script boundaries
    assert get_analyzer('af').code != 'nl' # this match is not close enough


@pytest.mark.parametrize('analyzer_class', LANGUAGES)
def test_language_analyzers_no_errors(analyzer_class):
    '''
    Check that all analyzers can at least be constructed, and their public
    methods can be called without runtime errors.
    '''

    analyzer = analyzer_class()
    analyzer.code
    analyzer.has_stopwords
    analyzer.has_stemming
    analyzer.char_filters()
    analyzer.token_filters()
    analyzer.analyzers()
    analyzer.standard_analyzer_name
    analyzer.clean_analyzer_name
    analyzer.stemmed_analyzer_name
    analyzer.stopwords()
