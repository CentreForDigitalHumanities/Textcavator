from time import sleep
from addcorpus.models import Corpus
from es.models import Index
from es.search import get_index, hits, total_hits
from indexing.models import IndexJob, CreateIndexTask, ReindexTask
from indexing.run_job import perform_indexing
from corpora_test.small.small_mock_corpus import SPECS

def test_reindex_task(small_mock_corpus, es_server, es_client, index_small_mock_corpus):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    current_index = Index.objects.get(server=es_server, name=get_index(small_mock_corpus))
    new_index = Index.objects.create(server=es_server, name='test-small-mock-corpus-reindex')

    job = IndexJob.objects.create(corpus=corpus)
    CreateIndexTask.objects.create(job=job, index=new_index)
    ReindexTask.objects.create(job=job, index=new_index, source_index=current_index)
    perform_indexing(job)
    sleep(1)

    result = es_client.search(index=new_index.name, query={'match_all': {}})
    assert total_hits(result) == SPECS['total_docs']
