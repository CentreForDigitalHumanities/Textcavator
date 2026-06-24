from datetime import datetime
import visualization.query as query
from es.search import search, hits

def test_date_manipulation(basic_query):
    assert query.get_filters(basic_query) == []

    # add date filter
    min_date = datetime(year = 1850, month = 1, day = 1)
    max_date = datetime(year = 1859, month = 12, day = 31)
    date_filter = query.make_date_filter(min_date, max_date)
    filtered_query = query.add_filter(basic_query, date_filter)
    assert query.get_filters(filtered_query) == [date_filter]
    query_min_date, query_max_date = query.get_date_range(filtered_query)
    assert query_min_date == min_date
    assert query_max_date == max_date

    # check old query is intact
    assert query.get_filters(basic_query) == []

    # add a more narrow date filter
    narrow_min_date = datetime(year = 1852, month = 1, day = 1)
    narrow_max_date = datetime(year = 1856, month = 12, day = 31)
    date_filter = query.make_date_filter(narrow_min_date, narrow_max_date)
    narrow_query = query.add_filter(filtered_query, date_filter)
    query_min_date, query_max_date = query.get_date_range(narrow_query)
    assert query_min_date == narrow_min_date
    assert query_max_date == narrow_max_date

    # add a wider date filter
    wide_min_date = datetime(year = 1840, month = 1, day = 1)
    wide_max_date = datetime(year = 1880, month = 12, day = 31)
    date_filter = query.make_date_filter(wide_min_date, wide_max_date)
    wide_query = query.add_filter(filtered_query, date_filter)
    query_min_date, query_max_date = query.get_date_range(wide_query)
    assert query_min_date == min_date
    assert query_max_date == max_date

def test_search(small_mock_corpus, es_client, index_small_mock_corpus, basic_query):
    """
    Test some search requests based on queries manipulated in the query module
    """
    query_no_text = query.remove_query(basic_query)
    result = search(
        corpus_name = small_mock_corpus,
        query_model=query_no_text,
        client=es_client,
    )
    assert len(hits(result)) == 3

    min_date = datetime(year = 1850, month = 1, day = 1)
    max_date = datetime(year = 1899, month = 12, day = 31)
    date_filter = query.make_date_filter(min_date, max_date)
    query_no_text = query.add_filter(query_no_text, date_filter)

    result = search(
        corpus_name = small_mock_corpus,
        query_model = query_no_text,
        client=es_client
    )

    assert len(hits(result)) == 1

def test_manipulation_is_pure(basic_query):
    narrow_timeframe = datetime(1850, 1, 1), datetime(1860, 12, 31)

    narrow_query = query.add_filter(
        basic_query,
        query.make_date_filter(*narrow_timeframe)
    )

    wide_timeframe = datetime(1800, 1, 1), datetime(1899, 12, 31)
    wide_query = query.add_filter(
        basic_query,
        query.make_date_filter(*wide_timeframe)
    )

    # operations should be pure functions: original objects should be unchanged
    assert query.get_date_range(basic_query) == (None, None)
    assert query.get_date_range(narrow_query) == narrow_timeframe
    assert query.get_date_range(wide_query) == wide_timeframe

def test_is_date_filter():
    assert query.is_date_filter({
        'range': {
            'date': {
                'gte': '1950-01-01',
                'lte': '1959-12-31',
                'format': 'yyyy-MM-dd'
            }
        }
    })

    assert query.is_date_filter({
        'range': {
            'publication_date': {
                'gte': '1950-01-01',
                'lte': '1959-12-31',
                'format': 'yyyy-MM-dd'
            }
        }
    })

    assert not query.is_date_filter({
        'range': {
            'year': {
                'gte': 1950,
                'lte': 1959,
            }
        }
    })

def test_get_date_range():
    min_date = datetime(1800, 1, 1)
    max_date = datetime(1900, 1, 1)
    date_filter = query.make_date_filter(min_date, max_date, 'publication_date')
    q = query.add_filter(query.MATCH_ALL, date_filter)
    assert query.get_date_range(q) == (min_date, max_date)
