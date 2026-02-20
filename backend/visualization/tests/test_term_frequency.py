import pytest
from visualization import term_frequency
from es.search import search, hits
import pytest
from visualization.conftest import MockClient

def test_extract_data_for_term_frequency(small_mock_corpus):
    es_query = make_query('test', ['content', 'title'])
    search_fields, aggregators = term_frequency.extract_data_for_term_frequency(small_mock_corpus, es_query)

    # fieldnames should look at specified fields
    target_fields = ['content', 'title']
    assert set(target_fields) == set(search_fields)

    # no .length multifield for all fields, so no aggregator
    assert aggregators == None

    # restrict the search field to one with token counts
    fields_with_token_counts = ['content']
    es_query = make_query('test', fields_with_token_counts)
    fieldnames, aggregators = term_frequency.extract_data_for_term_frequency(small_mock_corpus, es_query)

    # fieldnames should be restricted as well
    assert set(fields_with_token_counts) == set(fieldnames)

    # token count aggregator should be included
    aggregators_target = {
        'token_count_content': {
            'sum': {
                'field': 'content.length'
            }
        }
    }
    assert aggregators == aggregators_target


frequencies = [
    ('Alice', 2), # 1 in alice in wonderland title, 1 in its content
    ('rejoice', 1), # 1 in content of frankenstein
    ('evil forebodings', 2), # multiword, each occurs once
    ('evil + forebodings', 2), # + does nothing
    ('"evil forebodings"', 1), # 1 match for prhase
    ('"Alice in Wonderland" Frankenstein', 2),
    ('of', 5), # matches in multiple documents
    ('of Alice', 7),
    ('of + Alice', 4), # only get hits for 'of' in documents that also contain 'Alice'
    ('rejuice~1', 1), #fuzzy match
    ('hav*', 2), # wildcard match
    ('sit* hav*' , 3),
    ('-sit* hav*' , 2),
    ('-sit* + hav*' , 1),
    ('nomatches', 0),
]

@pytest.mark.parametrize('query_text,expected_count', frequencies)
def test_match_count(small_mock_corpus, es_client, index_small_mock_corpus, query_text, expected_count):
    """Test counting matches of the search term"""

    query = make_query(query_text=query_text)
    fieldnames, aggregators = term_frequency.extract_data_for_term_frequency(small_mock_corpus, query)
    match_count = term_frequency.get_match_count(es_client, query, small_mock_corpus, 100, fieldnames)
    assert match_count == expected_count

@pytest.fixture()
def fix_match_count(monkeypatch):
    def count_matches_alt(hits, *args, **kwargs):
        for hit in hits:
            yield 10

    monkeypatch.setattr(term_frequency, 'count_matches_in_documents', count_matches_alt)


def test_match_count_estimate(small_mock_corpus, basic_query, fix_match_count):
    client = MockClient(5000)
    matches = term_frequency.get_match_count(client, basic_query, small_mock_corpus, 1000, ['test'])
    # client gives 5,000 total hits and 10,000 terms for the 1,000 document sample
    # it estimates (10 - 1) * 4000 / 2 + 4000 = 22000 terms for the uncounted documents
    assert matches == 32000

def test_match_count_full(small_mock_corpus, basic_query, fix_match_count):
    client = MockClient(500)
    matches = term_frequency.get_match_count(client, basic_query, small_mock_corpus, 1000, ['test'])
    # client gives 500 total hits and 5000 terms (fully counted)
    assert matches == 5000

def test_total_docs_and_tokens(es_client, mock_corpus, index_mock_corpus, mock_corpus_specs):
    """Test total document counter"""
    query = make_query(query_text='*', search_in_fields=['content'])

    fieldnames, aggregators = term_frequency.extract_data_for_term_frequency(mock_corpus, query)
    total_doc_count, token_count = term_frequency.get_total_docs_and_tokens(es_client, query, mock_corpus, aggregators)
    assert total_doc_count == mock_corpus_specs['total_docs']
    assert token_count == (mock_corpus_specs['total_words'] if mock_corpus_specs['has_token_counts'] else None)

def test_term_frequency(small_mock_corpus, index_small_mock_corpus, small_mock_corpus_specs,):

    ## search in all fields
    query = make_query(query_text='Alice')
    match_count, total_doc_count, token_count = term_frequency.get_term_frequency(query, small_mock_corpus, 100)

    assert match_count == 2
    assert total_doc_count == small_mock_corpus_specs['total_docs']
    assert token_count == None

    ## search in content (includes token count)
    query = make_query(query_text='Alice', search_in_fields=['content'])
    match_count, total_doc_count, token_count = term_frequency.get_term_frequency(query, small_mock_corpus, 100)

    assert match_count == 1
    assert total_doc_count == small_mock_corpus_specs['total_docs']
    assert token_count == small_mock_corpus_specs['total_words']

def test_histogram_term_frequency(small_mock_corpus, index_small_mock_corpus):

    cases = [
        {
            'genre': 'Children',
            'matches': 2,
            'tokens': 21
        }, {
            'genre': 'Romance',
            'matches': 2,
            'tokens': 23,
        }, {
            'genre': 'Science fiction',
            'matches': 1,
            'tokens': 23
        }
    ]

    for case in cases:
        query = make_query(query_text='of', search_in_fields=['content'])
        result = term_frequency.get_aggregate_term_frequency(query, small_mock_corpus, 'genre', case['genre'])

        assert result == {
            'key': case['genre'],
            'match_count': case['matches'],
            'total_doc_count': 1,
            'token_count': case['tokens']
        }

def test_timeline_term_frequency(small_mock_corpus, index_small_mock_corpus):

    cases = [
        {
            'min_date': '1800-01-01',
            'max_date': '1850-01-01',
            'matches': 3,
            'tokens': 46,
            'doc': 2,
        }
    ]

    for case in cases:
        query = make_query(query_text='of', search_in_fields=['content'])
        result = term_frequency.get_date_term_frequency(query, small_mock_corpus, 'date', case['min_date'], case['max_date'])

        assert result == {
            'key': case['min_date'],
            'key_as_string': case['min_date'],
            'match_count': case['matches'],
            'total_doc_count': 2,
            'token_count': case['tokens']
        }


def make_query(query_text=None, search_in_fields=None):
    query = {
        "query": {
            "bool": {
                "filter": []
            }
        }
    }

    if query_text:
        query['query']['bool']['must'] = {
            "simple_query_string": {
                "query": query_text,
                "lenient": True,
                "default_operator": "or"
            }
        }

        if search_in_fields:
            query['query']['bool']['must']['simple_query_string']['fields'] = search_in_fields


    return query


term_count_cases = [
    ('disaster', 1),
    ('DISASTER', 1),
    ('disaster regarded', 2),
    ('disaster + regarded', 2),
    ('"evil forebodings"', 1),
    ('disaster "evil forebodings"', 2),
    ('disaster -regarded', 1),
    ('rejuice~2', 1),
]

@pytest.mark.parametrize('query_text,expected_count', term_count_cases)
def test_term_count_from_explain(small_mock_corpus, index_small_mock_corpus, query_text, expected_count):
    def query(query_text: str):
        return {
            "query": {
                "bool": {
                    "must": {
                        "simple_query_string": {
                            "query": query_text,
                            "fields": ["content"]
                        }
                    },
                    'filter': {
                        'term': { 'genre': 'Science fiction' },
                    }
                }
            },
            "explain": True,
        }

    result = search(small_mock_corpus, query(query_text))
    hit = hits(result)[0]
    count = term_frequency.count_matches_from_explanation(hit)
    assert count == expected_count
