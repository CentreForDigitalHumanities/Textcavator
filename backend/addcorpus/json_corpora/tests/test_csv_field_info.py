import os
from addcorpus.json_corpora.csv_field_info import (
    _is_date, _is_date_col, _is_long_text, get_csv_info, _is_url, _is_url_col
)
from addcorpus.python_corpora.load_corpus import load_corpus_definition


def test_is_url():
    assert _is_url('http://example.com')
    assert _is_url('https://example.com')
    assert not _is_url('www.example.com')
    assert not _is_url('not_a_url')
    assert not _is_url('')
    assert not _is_url('12345')


def test_is_url_col():
    clean_url_series = ['http://example.com', 'https://example.com']
    dirty_url_series = clean_url_series + ['']
    not_url_series = clean_url_series + ['', '12345']
    empty_series = ['', '']

    assert _is_url_col(clean_url_series)
    assert _is_url_col(dirty_url_series)
    assert not _is_url_col(not_url_series)
    assert not _is_url_col(empty_series)


def test_is_date():
    assert _is_date('2024-01-01')
    assert not _is_date('')
    assert not _is_date('5')
    assert not _is_date('01-01-2024')


def test_is_date_col():
    clean_date_series = ['1800-01-01', '2024-01-01']
    dirty_date_series = clean_date_series + ['']
    empty_series = ['', '']

    assert _is_date_col(clean_date_series)
    assert _is_date_col(dirty_date_series)
    assert not _is_date_col(empty_series)


def test_is_long_text():
    assert not _is_long_text('Example')
    assert _is_long_text('To be or not to be,\nThat is the question')
    assert _is_long_text(
        'It is a truth universally acknowledged, that a single man in possession of a ' \
        'good fortune must be in want of a wife. However little known the feelings or ' \
        'views of such a man may be on his first entering a neighbourhood, this truth ' \
        'is so well fixed in the minds of the surrounding families, that he is ' \
        'considered as the rightful property of some one or other of their daughters.',
    )
    assert not _is_long_text('')


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
