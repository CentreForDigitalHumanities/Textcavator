import itertools
import multiprocessing
import logging
import elasticsearch.helpers as es_helpers

from django import db
from django.conf import settings
from addcorpus.reader import make_reader
from indexing.models import PopulateIndexTask
from indexing.stop_job import raise_if_aborted

logger = logging.getLogger('indexing')

# copied from python docs (available in python >= 3.12)
# see: https://docs.python.org/3/library/itertools.html
def batched(iterable, n):
    "Batch data into tuples of length n. The last batch may be shorter."
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while (batch := tuple(itertools.islice(it, n))):
        yield batch


def process_batch(task_id, files):
    db.connections['default'].connect()

    task = PopulateIndexTask.objects.get(pk=task_id)
    reader = make_reader(task.corpus)
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

    server_config = task.index.server.configuration

    raise_if_aborted(task)

    # Do bulk operation
    client = task.client()
    for success, info in es_helpers.streaming_bulk(
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

    if settings.INDEX_MULTIPROCESSING:
        with multiprocessing.Pool() as pool:
            args = zip(itertools.repeat(task.pk), batched(files, settings.INDEX_BATCH_SIZE))
            pool.starmap(process_batch, args)
    else:
        process_batch(task.pk, files)
