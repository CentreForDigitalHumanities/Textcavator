import pytest

from visualization import simple_query_string

query_cases = [
    ('rejoice', ['rejoice']),
    ('evil forebodings',['evil', 'forebodings']),
    ('"evil forebodings"', ['"evil forebodings"']),
    ('regarded with "evil forebodings"', ['regarded', 'with', '"evil forebodings"']),
    ('evil + forebodings', ['evil', 'forebodings']),
    ('evil forebod*', ['evil', 'forebod*']),
    ('rejoice~1', ['rejoice~1']),
    ('rejoice~1 to hear', ['rejoice~1', 'to', 'hear']),
    ('rejoice + (evil | forebodings)', ['rejoice', 'evil', 'forebodings']),
    ('rejoice + ("evil forebodings" regarded)', ['rejoice', '"evil forebodings"', 'regarded']),
    ('"evil forebodings"~2 regarded', ['"evil forebodings"~2', 'regarded']),
    ('rejoice + (regarded | (evil + forebodings))', ['rejoice', 'regarded', 'evil', 'forebodings']),
    ('enterprise + -"evil forebodings"', ['enterprise', '-"evil forebodings"'])
]

@pytest.mark.parametrize('query_text,terms', query_cases)
def test_collect_terms(query_text, terms):
    components = simple_query_string.collect_terms(query_text)
    assert sorted(components) == sorted(terms) # ignore order

