import logging
from elasticsearch.helpers import streaming_bulk

from indexing.run_create_task import make_es_settings
from addcorpus.es_mappings import int_mapping, keyword_mapping
from addcorpus.models import CorpusConfiguration, Field, FieldDisplayTypes
from analysis.models import CreateTokenIndexTask, PopulateTokenIndexTask
from analysis.collect import token_docs
from indexing.stop_job import raise_if_aborted

logger = logging.getLogger('indexing')



def token_index_mapping(corpus_config: CorpusConfiguration):
    mappings = {
        ':token': keyword_mapping(),
        ':count': int_mapping(),
        ':doc_id': keyword_mapping(),
    }
    for field in corpus_config.fields.all():
        field: Field = field
        if field.display_type == FieldDisplayTypes.TEXT_CONTENT:
            field_mapping = field.es_mapping
            field_mapping.pop('term_vector', None)

            multifields = {
                name: conf
                for name, conf in field_mapping.get('fields', {}).items()
                if name in ['clean', 'stemmed']
            }
            for conf in multifields.values():
                conf.pop('term_vector', None)
            field_mapping['fields'] = multifields
            mappings[field.name] = field_mapping

        elif field.display_type == FieldDisplayTypes.TEXT:
            pass
        else:
            # TODO: only include aggregation-relevant fields
            mappings[field.name] = field.es_mapping
    return { 'properties': mappings }


def create_token_index(task: CreateTokenIndexTask):
    client = task.client()
    corpus_config: CorpusConfiguration = task.corpus.configuration
    index_name = task.index.name

    if client.indices.exists(index=index_name, allow_no_indices=False):
        if task.delete_existing:
            logger.info(
                'Deleting existing index: %s',
                index_name,
            )
            client.indices.delete(index=index_name, allow_no_indices=False)
        else:
            logger.error(
                'Index %s already exists; delete it or set delete_existing on the task',
                index_name
            )
            raise Exception('index already exists')

    settings = make_es_settings(task.corpus)
    mappings = token_index_mapping(corpus_config)

    client.indices.create(
        index=index_name,
        settings=settings,
        mappings=mappings,
    )

    return index_name


def populate_token_index(task: PopulateTokenIndexTask):
    # Obtain source documents
    docs = token_docs(task.corpus, task.source_index.name)

    actions = (
        {
            "_op_type": "index",
            "_index": task.index.name,
            "_source": doc,
        }
        for doc in docs
    )

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
