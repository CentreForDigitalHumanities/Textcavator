from typing import Optional
import logging

from indexing.run_create_task import make_es_settings
from addcorpus.models import CorpusConfiguration, Field, FieldDisplayTypes
from analysis.models import CreateFrequencyIndexTask, PopulateFrequencyIndexTask

logger = logging.getLogger('indexing')


def token_index_name(source_index_name: str):
    return source_index_name + '-tokens'


def token_field_name(field_name: str, multifield: Optional[str] = None,  size: int = 1):
    if multifield:
        return ':'.join([field_name, multifield, size])
    return ':'.join([field_name, size])


def token_index_mapping(corpus_config: CorpusConfiguration):
    mappings = {}
    for field in corpus_config.fields:
        field: Field = field
        if field.display_type == FieldDisplayTypes.TEXT_CONTENT:
            name = token_field_name(field.name, 1)
            mapping = field.es_mapping
            multifields = mappings.pop('fields', {})
            mappings[name] = mapping
            for multifield in multifields:
                if multifield in ['clean', 'stemmed']:
                    name = token_field_name(field.name, multifield, 1)
                    mappings[name] = multifields[multifield]
        else:
            # TODO: only include aggregation-relevant fields
            mappings[field.name] = field.es_mapping


def create_token_index(task: CreateFrequencyIndexTask):
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


def populate_frequency_index(task: PopulateFrequencyIndexTask):
    pass
