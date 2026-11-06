import logging
from elasticsearch.helpers import streaming_bulk
from typing import Iterable, Dict

from addcorpus.reader import make_reader
from indexing.models import PopulateIndexTask, IndexTask
from indexing.stop_job import raise_if_aborted

logger = logging.getLogger('indexing')


def populate(task: PopulateIndexTask):
    '''
    Populate an ElasticSearch index from the corpus' source files.
    '''
    reader = make_reader(task.corpus)

    logger.info('Attempting to populate index...')

    # Obtain source documents
    files = reader.sources(
        start=task.document_min_date,
        end=task.document_max_date)
    docs = reader.documents(files)

    # Each source document is decorated as an indexing operation, so that it
    # can be sent to ElasticSearch in bulk
    actions = (
        {
            "_op_type": "index",
            "_index": task.index.name,
            "_id": doc.get("id"),
            "_source": doc,
        }
        for doc in docs
    )
    run_bulk(task, actions)


def run_bulk(task: IndexTask, actions: Iterable[Dict]):
    server_config = task.index.server.configuration

    raise_if_aborted(task)

    # Do bulk operation
    client = task.client()
    for success, info in streaming_bulk(
        client,
        actions,
        chunk_size=server_config["chunk_size"],
        max_chunk_bytes=server_config["max_chunk_bytes"],
        raise_on_exception=False,
        raise_on_error=False,
    ):
        if not success:
            logger.error(f"FAILED INDEX: {info}")
        raise_if_aborted(task)
