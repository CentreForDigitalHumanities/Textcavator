from es.client import elasticsearch
from visualization.query import MATCH_ALL
from es.search import get_index, hits, total_hits
from bow.index_utils import bow_field_name
from visualization.termvectors import get_terms, request_termvectors_batched

def test_bow_indexing(small_mock_corpus, index_small_mock_corpus, index_small_mock_corpus_bow):
    client = elasticsearch(small_mock_corpus)
    index = get_index(small_mock_corpus)
    results = client.search(
        index=index,
        **MATCH_ALL,
    )
    assert total_hits(results) == 3
    for hit in hits(results):
        assert len(hit['_source'][bow_field_name('content')])

    for doc, vectors in request_termvectors_batched(hits(results), client, True, ['content']):
        tokens = doc['_source'][bow_field_name('content')]
        term_vectors = get_terms(vectors, 'content')
        for token in tokens:
            term = token[':token']
            assert token[':count'] == term_vectors[term]['term_freq']
