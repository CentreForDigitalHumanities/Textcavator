from addcorpus.models import Corpus
from indexing.constants import TaskStatus
from indexing.health_check import CorpusIndexHealth

def test_health_check_not_indexed(mock_corpus, es_index_client, es_server):
    corpus = Corpus.objects.get(name=mock_corpus)
    health = CorpusIndexHealth(corpus)
    assert health.server_active
    assert health.index_active is False
    assert health.settings_compatible is None
    assert health.mappings_compatible is None
    assert health.job_status is None
    assert health.includes_latest_data is None
    assert health.corpus_ready_to_index

def test_health_check_index_python_corpus(small_mock_corpus, index_small_mock_corpus, es_server):
    corpus = Corpus.objects.get(name=small_mock_corpus)
    health = CorpusIndexHealth(corpus)
    assert health.server_active
    assert health.index_active
    assert health.settings_compatible
    assert health.mappings_compatible
    assert health.job_status == TaskStatus.DONE
    assert health.includes_latest_data is None # this is a python corpus, so NA
    assert health.corpus_ready_to_index

def test_health_check_indexed_db_corpus(json_mock_corpus, index_json_mock_corpus, es_server):
    health = CorpusIndexHealth(json_mock_corpus)
    assert health.server_active
    assert health.index_active
    assert health.settings_compatible
    assert health.mappings_compatible
    assert health.job_status == TaskStatus.DONE
    assert health.includes_latest_data
    assert health.corpus_ready_to_index
