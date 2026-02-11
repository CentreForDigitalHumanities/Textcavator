from time import sleep
from elasticsearch import Elasticsearch
import pytest

from indexing.run_job import perform_indexing
from indexing.create_job import create_indexing_job
from es.sync import (
    update_server_table_from_settings, fetch_index_metadata, update_availability
)
from es.models import Index, Server
from es.search import get_index
from addcorpus.models import Corpus

def test_update_server_data(settings, db):
    update_server_table_from_settings()

    # test settings always include "default" server
    default_server = Server.objects.get(name='default')
    assert default_server.active

    # remove server from settings
    conf = settings.SERVERS.pop('default')
    update_server_table_from_settings()
    default_server.refresh_from_db()
    assert not default_server.active

    # add server to settings again
    settings.SERVERS['default'] = conf
    update_server_table_from_settings()
    default_server.refresh_from_db()
    assert default_server.active

@pytest.mark.filterwarnings("ignore:Corpus has no 'id' field")
def test_fetch_index_data(db, es_client, basic_mock_corpus, index_basic_mock_corpus):
    update_server_table_from_settings()
    fetch_index_metadata()

    corpus = Corpus.objects.get(name=basic_mock_corpus)
    index = Index.objects.get(server__name='default', name=get_index(basic_mock_corpus))
    assert index.available

    es_client.indices.delete(index=index.name)
    fetch_index_metadata()
    index.refresh_from_db()
    assert not index.available

    # restore index
    job = create_indexing_job(corpus)
    perform_indexing(job)
    sleep(1)

    fetch_index_metadata()
    index.refresh_from_db()
    assert index.available


def test_update_index_availability(db, es_client: Elasticsearch, test_index_cleanup):
    name = 'test-index-availability-1'
    es_client.indices.create(index=name)

    update_server_table_from_settings()
    fetch_index_metadata()

    index = Index.objects.get(server__name='default', name=name)

    # case: index is available
    update_availability(index)
    assert index.available

    # case: index is not available
    es_client.indices.delete(index=name)
    update_availability(index)
    assert not index.available

    # case: index is not available, but its name matches the alias of another index
    es_client.indices.create(
        index='test-index-availability-2',
        aliases={ name: {} },
    )
    update_availability(index)
    assert not index.available
