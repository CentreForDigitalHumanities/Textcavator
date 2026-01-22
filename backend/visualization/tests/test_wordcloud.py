import visualization.wordcloud as wordcloud
from es import search
import pytest
import visualization.query as query
from datetime import datetime


def make_filtered_query():
    empty_query = {
        "query": {
            "bool": {
                "filter": []
            }
        }
    }
    datefilter = query.make_date_filter(
        max_date=datetime(year=1820, month=12, day=31))
    return query.add_filter(empty_query, datefilter)


@pytest.fixture()
def small_mock_corpus_complete_wordcloud(small_mock_corpus, index_small_mock_corpus):
    result = search.search(
        corpus_name=small_mock_corpus,
        query_model=query.MATCH_ALL,
        size=10
    )

    documents = search.hits(result)
    return wordcloud.make_wordcloud_data(documents, 'content', small_mock_corpus)


def test_wordcloud(small_mock_corpus, small_mock_corpus_complete_wordcloud):

    target_unfiltered = [
        {'key': 'wife', 'doc_count': 1},
        {'key': 'universally', 'doc_count': 1},
        {'key': 'truth', 'doc_count': 1},
        {'key': 'tired', 'doc_count': 1},
        {'key': 'sitting', 'doc_count': 1},
        {'key': 'sister', 'doc_count': 1},
        {'key': 'single', 'doc_count': 1},
        {'key': 'rejoice', 'doc_count': 1},
        {'key': 'regarded', 'doc_count': 1},
        {'key': 'possession', 'doc_count': 1},
        {'key': 'nothing', 'doc_count': 1},
        {'key': 'man', 'doc_count': 1},
        {'key': 'hear', 'doc_count': 1},
        {'key': 'good', 'doc_count': 1},
        {'key': 'fortune', 'doc_count': 1},
        {'key': 'forebodings', 'doc_count': 1},
        {'key': 'evil', 'doc_count': 1},
        {'key': 'enterprise', 'doc_count': 1},
        {'key': 'disaster', 'doc_count': 1},
        {'key': 'commencement', 'doc_count': 1},
        {'key': 'beginning', 'doc_count': 1},
        {'key': 'bank', 'doc_count': 1},
        {'key': 'alice', 'doc_count': 1},
        {'key': 'acknowledged', 'doc_count': 1},
        {'key': 'accompanied', 'doc_count': 1}
    ]

    for item in target_unfiltered:
        term = item['key']
        doc_count = item['doc_count']
        match = next(
            hit for hit in small_mock_corpus_complete_wordcloud if hit['key'] == term)
        assert match
        assert doc_count == match['doc_count']


def test_wordcloud_filtered(small_mock_corpus, es_client, index_small_mock_corpus):
    """Test the word cloud on a query with date filter"""

    filtered_query = make_filtered_query()

    result = search.search(
        corpus_name=small_mock_corpus,
        query_model=filtered_query,
        size=10,
        client=es_client
    )

    documents = search.hits(result)
    output = wordcloud.make_wordcloud_data(
        documents, 'content', small_mock_corpus)

    # from frankenstein + pride & prejudice
    words_to_include = ['accompanied', 'acknowledged', 'truth', 'universally']
    words_to_exclude = ['alice', 'beginning']  # from alice in wonderland

    def occurs_in_results(word): return any(
        item['key'] == word for item in output)

    for word in words_to_include:
        assert occurs_in_results(word)

    for word in words_to_exclude:
        assert not occurs_in_results(word)

def test_wordcloud_counts(small_mock_corpus):
    '''
    Each non-stopword only occurs once in the mock corpus data, so
    this test uses some fake texts for counting.
    '''

    texts = [
        'Some words',
        'Even more!',
        'Words, words, words...',
        'More words! More!',
        'That should be enough.',
    ]
    docs = [
        {'_source': {'content': text}}
        for text in texts
    ]

    results = wordcloud.make_wordcloud_data(docs, 'content', small_mock_corpus)

    counts = {
        item['key']: item['doc_count']
        for item in results
    }

    assert counts['words'] == 5

def test_wordcloud_filters_stopwords(small_mock_corpus, small_mock_corpus_complete_wordcloud):
    stopwords = ['the', 'and', 'of']
    for stopword in stopwords:
        match = any(
            item['key'] == stopword for item in small_mock_corpus_complete_wordcloud)
        assert not match
