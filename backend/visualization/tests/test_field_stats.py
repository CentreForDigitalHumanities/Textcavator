from visualization.field_stats import count_field, count_total, report_coverage, report_cardinality


def test_count(small_mock_corpus, es_client, index_small_mock_corpus, small_mock_corpus_specs):
    total_docs = small_mock_corpus_specs['total_docs']

    for field in small_mock_corpus_specs['fields']:
        count = count_field(es_client, small_mock_corpus, field)
        assert count == total_docs

    assert count_total(es_client, small_mock_corpus) == total_docs


def test_report(small_mock_corpus, es_client, index_small_mock_corpus, small_mock_corpus_specs):
    report = report_coverage(small_mock_corpus)

    assert report == {
        'date': 1.0,
        'title': 1.0,
        'content': 1.0,
        'genre': 1.0,
    }

def test_cardinality(small_mock_corpus, es_client, index_small_mock_corpus, small_mock_corpus_specs):
    report = report_cardinality(small_mock_corpus)
    assert report == {
        'genre': 3
    }
