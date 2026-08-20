from time import sleep
from addcorpus.models import Corpus
from bow.create_index_job import create_bow_index_job
from es.client import elasticsearch
from indexing.run_job import perform_indexing
from visualization.query import MATCH_ALL
from es.search import get_index, hits, total_hits
from bow.index_utils import bow_field_name
from visualization.termvectors import get_terms, request_termvectors_batched

def test_bow_indexing(small_mock_corpus, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    job = create_bow_index_job(corpus)
    perform_indexing(job)
    sleep(1)

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
            assert token[':total_count'] == term_vectors[term]['ttf']
