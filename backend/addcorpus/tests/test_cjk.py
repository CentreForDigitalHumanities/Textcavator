from es.client import elasticsearch
from es.search import search, hits, get_index
from visualization.query import MATCH_ALL

def test_cjk_language_analysis(cjk_mock_corpus: str, index_cjk_mock_corpus):
    client = elasticsearch(cjk_mock_corpus)
    results = hits(search(cjk_mock_corpus, MATCH_ALL, client))
    doc_id = results[0]['_id']
    vectors = client.termvectors(index=get_index(cjk_mock_corpus), id=doc_id).body['term_vectors']
    assert len(vectors['content']['terms']) == 21
    assert len(vectors['content.clean']['terms']) == 16
