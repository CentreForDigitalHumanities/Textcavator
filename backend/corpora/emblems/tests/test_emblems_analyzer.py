from elasticsearch import Elasticsearch
from corpora.emblems.analyzer import CustomEmblemsAnalyzer
from addcorpus.tests.test_language_analysis import analyzer_test_output

def test_custom_emblems_analyzer():
    analyzer = CustomEmblemsAnalyzer()
    assert 'standard_unk' in analyzer.analyzers()

_analysis_cases = [
    ('Elle travaille à sa ruïne', ['elle', 'travaille', 'a', 'sa', 'ruine']),
    ('hæc', ['haec']),
]


def test_custom_emblems_analyzer_matching(es_client: Elasticsearch, test_index_cleanup):
    analyzer = CustomEmblemsAnalyzer()
    index_name = f'test-analyzers-{analyzer.code}'
    settings = {
        'index': {'number_of_shards': 1, 'number_of_replicas': 1},
        'analysis': {
            'char_filter': analyzer.char_filters(),
            'filter': analyzer.token_filters(),
            'analyzer': analyzer.analyzers(),
        },
    }
    es_client.indices.create(index=index_name, settings=settings)
    for content, expected in _analysis_cases:
        tokens = analyzer_test_output(
            es_client,
            index_name,
            analyzer.standard_analyzer_name,
            content
        )
        assert tokens == expected
