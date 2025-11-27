import os
from addcorpus.json_corpora.csv_field_info import (
    is_date, is_date_col, is_long_text, get_csv_info, is_url, is_url_col
)
import pandas as pd
from addcorpus.python_corpora.load_corpus import load_corpus_definition


def test_is_url():
    assert is_url('http://example.com')
    assert is_url('https://example.com')
    assert not is_url('www.example.com')
    assert not is_url('not_a_url')
    assert not is_url(None)
    assert not is_url(12345)


def test_is_url_col():
    clean_url_series = pd.Series(['http://example.com', 'https://example.com'])
    dirty_url_series = pd.concat([clean_url_series, pd.Series([None, ''])])
    not_url_series = pd.concat([clean_url_series, pd.Series([None, 12345])])
    empty_series = pd.Series([None, None])

    assert is_url_col(clean_url_series)
    assert is_url_col(dirty_url_series)
    assert not is_url_col(not_url_series)
    assert not is_url_col(empty_series)


def test_is_date():
    assert is_date('2024-01-01')
    assert not is_date(None)
    assert not is_date(5)
    assert not is_date('01-01-2024')


def test_is_date_col():
    clean_date_series = pd.Series(['1800-01-01', '2024-01-01'])
    dirty_date_series = pd.concat([clean_date_series, pd.Series([None, ''])])
    empty_series = pd.Series([None, None])

    assert is_date_col(clean_date_series)
    assert is_date_col(dirty_date_series)
    assert not is_date_col(empty_series)


def test_is_long_text():
    assert not is_long_text('Example')
    assert is_long_text('To be or not to be,\nThat is the question')
    assert is_long_text(
        'It is a truth universally acknowledged, that a single man in possession of a good fortune must be in want of a wife.',
    )
    assert not is_long_text(None)


def test_map_col(small_mock_corpus):
    dir = load_corpus_definition(small_mock_corpus).data_directory
    filepath = os.path.join(dir, 'example.csv')
    info = get_csv_info(filepath)
    assert info == {
        'n_rows': 3,
        'fields': [
            {'name': 'date', 'type': 'date'},
            {'name': 'genre', 'type': 'text_metadata'},
            {'name': 'title', 'type': 'text_metadata'},
            {'name': 'content', 'type': 'text_content'},
            {'name': 'url', 'type': 'url'}
        ],
        'delimiter': ','
    }
