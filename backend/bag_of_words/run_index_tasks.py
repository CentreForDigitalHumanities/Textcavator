import logging
from copy import copy
from elasticsearch.helpers import streaming_bulk
from typing import TYPE_CHECKING

from bag_of_words.index_utils import bow_field_name
from addcorpus.es_mappings import int_mapping, keyword_mapping
from addcorpus.models import  Field
from bag_of_words.collect import token_data
from indexing.stop_job import raise_if_aborted

if TYPE_CHECKING:
    from bag_of_words.models import AddBOWFieldTask, PopulateBOWFieldTask

logger = logging.getLogger('indexing')

def nested_bow_mapping(field: Field):
    token_mappings = {
        ':token': keyword_mapping(),
        ':count': int_mapping(),
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


def add_bow_field(task: 'AddBOWFieldTask') -> None:
    client = task.client()
    index_name = task.index.name

    if not client.indices.exists(index=index_name, allow_no_indices=False):
        logger.error('Index %s does not exist', index_name)
        raise Exception('Index does not exist')

    mapping = { bow_field_name(task.field.name): nested_bow_mapping(task.field)}

    client.indices.put_mapping(
        index=index_name,
        allow_no_indices=False,
        properties=mapping,
    )


def populate_bow_field(task: 'PopulateBOWFieldTask'):
    # Obtain source documents
    docs = token_data(task.corpus, task.index.name, task.field.name)

    actions = (
        {
            '_op_type': 'update',
            '_index': task.index.name,
            '_id': doc_id,
            'doc': data,
        }
        for doc_id, data in docs
    )

    client = task.client()
    server_config = task.index.server.configuration
    raise_if_aborted(task)

    # Do bulk operation
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
