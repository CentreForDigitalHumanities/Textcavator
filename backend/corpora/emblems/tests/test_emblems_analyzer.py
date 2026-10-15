from elasticsearch import Elasticsearch
from corpora.emblems.analyzer import CustomEmblemsAnalyzer

def test_custom_emblems_analyzer():
    analyzer = CustomEmblemsAnalyzer()
    assert 'standard_unk' in analyzer.analyzers()

_analysis_cases = [
    ('Elle travaille à sa ruïne', ['elle', 'travaille', 'a', 'sa', 'ruine']),
    ('hæc', ['haec']),
]

def test_custom_emblems_analyzer_matching(es_client: Elasticsearch):
    analyzer = CustomEmblemsAnalyzer()
    for content, expected in _analysis_cases:
        result = es_client.indices.analyze(
            text=content,
            **analyzer._standard_analyzer(),
        )
        tokens = [token['token'] for token in result.body['tokens']]
        assert tokens == expected
