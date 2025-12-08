from visualization.query import MATCH_ALL
import pytest
from rest_framework import status

@pytest.fixture()
def wordcloud_body(mock_corpus):
    return {
        'corpus': mock_corpus,
        'field': 'content',
        'es_query': MATCH_ALL,
        'size': 1000,
    }

def test_wordcloud_view(admin_client, mock_corpus, index_mock_corpus, wordcloud_body):
    response =admin_client.post(
        '/api/visualization/wordcloud',
        wordcloud_body,
        content_type='application/json'
    )
    assert status.is_success(response.status_code)

@pytest.fixture
def date_term_frequency_body(basic_query, small_mock_corpus):
    return {
        'es_query': basic_query,
        'corpus_name': small_mock_corpus,
        'field_name': 'date',
        'bins': [
            {
                'start_date': '1850-01-01',
                'end_date': '1850-12-31',
                'size': 10,
            }, {
                'start_date': '1851-01-01',
                'end_date': '1851-12-31',
                'size': 10,

            }
        ]

    }

@pytest.fixture
def aggregate_term_frequency_body(basic_query, small_mock_corpus):
    return {
        'es_query': basic_query,
        'corpus_name': small_mock_corpus,
        'field_name': 'genre',
        'bins': [
            { 'field_value': 'Romance', 'size': 10 },
            { 'field_value': 'Science fiction', 'size': 10 },
            { 'field_value': 'Children', 'size': 10 },
        ]
    }

@pytest.fixture
def ngram_body(basic_query, small_mock_corpus):
    return {
        'es_query': basic_query,
        'corpus_name': small_mock_corpus,
        'field': 'content',
        'ngram_size': 2,
        'term_position': [0, 1],
        'freq_compensation': True,
        'subfield': 'clean',
        'max_size_per_interval': 2,
        'number_of_ngrams': 10,
        'date_field': 'date',
    }

def test_ngrams(transactional_db, admin_client, ngram_body, index_small_mock_corpus, celery_worker):
    post_response = admin_client.post('/api/visualization/ngram', ngram_body, content_type='application/json')
    assert post_response.status_code == 200

def test_aggregate_term_frequency(transactional_db, admin_client, aggregate_term_frequency_body, index_small_mock_corpus, celery_worker):
    post_response = admin_client.post('/api/visualization/aggregate_term_frequency', aggregate_term_frequency_body, content_type='application/json')
    assert post_response.status_code == 200
    del aggregate_term_frequency_body['es_query']
    post_response = admin_client.post('/api/visualization/aggregate_term_frequency', aggregate_term_frequency_body, content_type='application/json')
    assert post_response.status_code == 400

def test_date_term_frequency(transactional_db, admin_client, date_term_frequency_body, index_small_mock_corpus, celery_worker):
    post_response = admin_client.post('/api/visualization/date_term_frequency', date_term_frequency_body, content_type='application/json')
    assert post_response.status_code == 200
    del date_term_frequency_body['es_query']
    post_response = admin_client.post('/api/visualization/date_term_frequency', date_term_frequency_body, content_type='application/json')
    assert post_response.status_code == 400

def test_term_frequency_limit(transactional_db, admin_client, date_term_frequency_body, aggregate_term_frequency_body, index_small_mock_corpus, celery_worker):
    for bin in date_term_frequency_body['bins']:
        bin['size'] = 1000000
    post_response = admin_client.post('/api/visualization/date_term_frequency', date_term_frequency_body, content_type='application/json')
    assert post_response.status_code == 400

    for bin in aggregate_term_frequency_body['bins']:
        bin['size'] = 1000000
    post_response = admin_client.post('/api/visualization/aggregate_term_frequency', aggregate_term_frequency_body, content_type='application/json')
    assert post_response.status_code == 400
