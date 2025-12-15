from typing import Optional, Tuple
import datetime
from django.db import transaction

from addcorpus.models import Corpus
from es.client import elasticsearch, server_for_corpus
from es.es_alias import (
    get_current_index_name,
    indices_with_alias
)
from es.versioning import next_version_number, highest_version_in_result, version_from_name
from indexing.models import (
    IndexJob, CreateIndexTask, PopulateIndexTask, UpdateIndexTask,
    RemoveAliasTask, AddAliasTask, UpdateSettingsTask, DeleteIndexTask,
)
from es.sync import update_server_table_from_settings
from es.models import Server, Index


@transaction.atomic
def create_indexing_job(
    corpus: Corpus,
    start: Optional[datetime.date] = None,
    end: Optional[datetime.date] = None,
    mappings_only: bool = False,
    add: bool = False,
    clear: bool = False,
    prod: bool = False,
    rollover: bool = False,
    update: bool = False,
) -> IndexJob:
    '''
    Create an IndexJob to index a corpus.

    Depending on parameters, this job may include creating an new index, adding documents,
    running an update script, and rolling over the alias. Parameters are described
    in detail in the documentation for the `index` command.
    '''
    create_new = not (add or update)

    update_server_table_from_settings()

    job = IndexJob.objects.create(corpus=corpus)
    server = _server_for_job(job)
    index, alias = _index_and_alias_for_job(job, prod, create_new)

    if create_new:
        CreateIndexTask.objects.create(
            job=job,
            index=index,
            production_settings=prod,
            delete_existing=clear,
        )

    if not (mappings_only or update):
        PopulateIndexTask.objects.create(
            job=job,
            index=index,
            document_min_date=start,
            document_max_date=end,
        )

    if update:
        UpdateIndexTask.objects.create(
            job=job,
            index=index,
            document_min_date=start,
            document_max_date=end,
        )

    if prod and create_new:
        UpdateSettingsTask.objects.create(
            job=job,
            index=index,
            settings={"number_of_replicas": 1},
        )

    if prod and rollover:
        for aliased_index in indices_with_alias(server, alias):
            RemoveAliasTask.objects.create(
                job=job,
                index=aliased_index,
                alias=alias,
            )
        AddAliasTask.objects.create(
            job=job,
            index=index,
            alias=alias,
        )

    return job


def _server_for_job(job: IndexJob):
    server_name = server_for_corpus(job.corpus.name)
    server = Server.objects.get(name=server_name)
    return server


def _index_and_alias_for_job(job: IndexJob, prod: bool, create_new: bool) -> Tuple[Index, str]:
    corpus = job.corpus
    server = _server_for_job(job)
    client = elasticsearch(corpus.name)
    base_name = _index_base_name(server, corpus)

    if prod:
        alias = corpus.configuration.es_alias or base_name
        if create_new:
            next_version = next_version_number(client, alias, base_name)
            versioned_name = f'{base_name}-{next_version}'
        else:
            versioned_name = get_current_index_name(
                corpus.configuration, client
            )

        index, _ = Index.objects.get_or_create(
            server=server, name=versioned_name
        )
    else:
        alias = None
        index, _ = Index.objects.get_or_create(
            server=server, name=base_name
        )

    return index, alias


def _index_base_name(server: Server, corpus: Corpus) -> str:
    if corpus.configuration.es_index:
        return corpus.configuration.es_index

    prefix = server.configuration.get('index_prefix', None)
    name = corpus.name if corpus.has_python_definition else f'custom_{corpus.pk}'
    return f'{prefix}-{name}' if prefix else name

@transaction.atomic
def create_alias_job(corpus: Corpus, clean=False) -> IndexJob:
    '''
    Create a job to move the alias of a corpus to the index with the highest version
    '''

    job = IndexJob.objects.create(corpus=corpus)

    corpus_config = corpus.configuration
    corpus_name = corpus.name
    update_server_table_from_settings()
    server = Server.objects.get(name=server_for_corpus(corpus_name))
    index_name = corpus_config.es_index
    index_alias = corpus_config.es_alias
    client = elasticsearch(corpus_name)

    alias = index_alias if index_alias else index_name
    indices = client.indices.get(index='{}-*'.format(index_name))
    highest_version = highest_version_in_result(indices, alias)

    for index_name, properties in indices.items():
        is_aliased = alias in properties['aliases'].keys()
        is_highest_version = version_from_name(index_name, alias) == highest_version
        index, _ = Index.objects.get_or_create(server=server, name=index_name)

        if not is_highest_version and clean:
            DeleteIndexTask.objects.create(job=job, index=index)

        if not is_highest_version and is_aliased and not clean:
            RemoveAliasTask.objects.create(job=job, index=index, alias=alias)

        if is_highest_version and not is_aliased:
            AddAliasTask.objects.create(job=job, index=index, alias=alias)

    return job
