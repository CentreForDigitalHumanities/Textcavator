from addcorpus.language_analysis import get_analyzer

def test_get_analyzer():
    assert get_analyzer('nl').code == 'nl'
    assert get_analyzer('nld').code == 'nl'
    assert get_analyzer('nl-BE').code == 'nl'
    assert get_analyzer('nl-Cyrl').code == 'und' # no ignoring script boundaries
    assert get_analyzer('af').code != 'nl' # this match is not close enough
