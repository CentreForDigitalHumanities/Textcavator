'''
Defines functionality to execute a CreateIndexTask
'''

from typing import Dict
import logging

from addcorpus.es_settings import es_settings
from addcorpus.models import Corpus, CorpusConfiguration
from addcorpus.python_corpora.load_corpus import load_corpus_definition
from indexing.models import (
    CreateIndexTask
)


logger = logging.getLogger('indexing')


def make_es_settings(corpus: Corpus) -> Dict:
    if corpus.has_python_definition:
        corpus_def = load_corpus_definition(corpus.name)
        return corpus_def.es_settings
    return es_settings(
        languages=corpus.configuration.languages
    )


def make_es_mapping(corpus_configuration: CorpusConfiguration) -> Dict:
    '''
    Create the ElasticSearch mapping for the fields of this corpus. May be
    passed to the body of an ElasticSearch index creation request.
    '''
    return {
        'properties': {
            field.name: field.es_mapping
            for field in corpus_configuration.fields.all()
            if field.es_mapping and field.indexed
        }
    }


def create(task: CreateIndexTask):
    client = task.client()

    corpus_config = task.corpus.configuration
    index_name = task.index.name
    es_mapping = make_es_mapping(corpus_config)

    if client.indices.exists(index=index_name, allow_no_indices=False):
        if task.delete_existing:
            logger.info('Attempting to clean old index...')
            client.indices.delete(index=index_name, allow_no_indices=False)
        else:
            logger.error(
                'Index `{}` already exists. Do you need to add an alias for it or '
                'perhaps delete it?'.format(index_name)
            )
            raise Exception('index already exists')

    settings = make_es_settings(task.corpus)

    if task.production_settings:
        logger.info('Adding prod settings to index')
        settings['index'].update({
            'number_of_replicas': 0,
            'number_of_shards': 5
        })

    logger.info('Attempting to create index `{}`...'.format(index_name))

    client.indices.create(
        index=task.index.name,
        settings=settings,
        mappings=es_mapping,
    )
    return index_name
