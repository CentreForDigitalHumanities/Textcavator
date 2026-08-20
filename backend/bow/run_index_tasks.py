import logging
from copy import copy
from elasticsearch.helpers import streaming_bulk
from typing import Dict

from indexing.run_create_task import make_es_settings
from bow.index_utils import bow_field_name
from addcorpus.es_mappings import int_mapping, keyword_mapping
from addcorpus.models import CorpusConfiguration, Field, FieldDisplayTypes
from bow.models import CreateBOWIndexTask, PopulateBOWIndexTask
from bow.collect import token_docs
from indexing.stop_job import raise_if_aborted

logger = logging.getLogger('indexing')

def nested_bow_mapping(field: Field):
    token_mappings = {
        ':token': keyword_mapping(),
        ':count': int_mapping(),
        ':total_count': int_mapping(),
    }

    field_mapping = copy(field.es_mapping)
    field_mapping.pop('term_vector', None)

    multifields = {
        name: conf
        for name, conf in field_mapping.get('fields', {}).items()
        if name in ['clean', 'stemmed']
    }
    for conf in multifields.values():
        conf.pop('term_vector', None)
    field_mapping['fields'] = multifields

    return {
        'type': 'nested',
        'dynamic': False,
        'properties': {field.name: field_mapping} | token_mappings,
    }


def bow_index_mapping(corpus_config: CorpusConfiguration) -> Dict:
    mappings = {
        ':id': keyword_mapping(),
    }

    for field in corpus_config.fields.all():
        field: Field = field
        if field.display_type == FieldDisplayTypes.TEXT_CONTENT:
            mappings[bow_field_name(field.name)] = nested_bow_mapping(field)
        elif field.display_type == FieldDisplayTypes.TEXT:
            pass
        else:
            # TODO: only include aggregation-relevant fields
            mappings[field.name] = field.es_mapping
    return { 'properties': mappings }

def bow_index_settings(task: CreateBOWIndexTask) -> Dict:
    settings = make_es_settings(task.corpus)
    settings['index'].update({
        'number_of_replicas': 0,
        'number_of_shards': 5
    })
    return settings

def create_bow_index(task: CreateBOWIndexTask) -> str:
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

    settings = bow_index_settings(task)
    mappings = bow_index_mapping(corpus_config)

    client.indices.create(
        index=index_name,
        settings=settings,
        mappings=mappings,
    )

    return index_name


def populate_bow_index(task: PopulateBOWIndexTask):
    # Obtain source documents
    docs = token_docs(task.corpus, task.source_index.name, threshold=task.threshold)

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
