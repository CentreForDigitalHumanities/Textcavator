from typing import Optional, Tuple
import datetime
from django.db import transaction

from addcorpus.models import Corpus
from es.client import elasticsearch, server_for_corpus
from es.es_alias import get_current_index_name, indices_with_alias
from es.versioning import (
    indices_with_base_name, next_version_number, highest_version_in_result,
    version_from_name
)
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
    index, base_name = _index_and_base_name_for_job(job, prod, create_new)

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
        _add_alias_rollover_tasks(job, server, base_name, index)

    if not prod:
        if alias := _extra_alias(job):
            AddAliasTask.objects.create(
                job=job, index=index, alias=alias
            )

    return job


def _add_alias_rollover_tasks(job: IndexJob, server: Server, base_name: str, new_index: Index) -> None:
    if base_name in indices_with_base_name(server.client(), base_name):
        raise Exception(f'Cannot rollover: existing index uses {base_name} as a name instead of an alias')

    AddAliasTask.objects.create(
        job=job,
        index=new_index,
        alias=base_name,
    )
    for aliased_index in indices_with_alias(server, base_name):
        RemoveAliasTask.objects.create(
            job=job,
            index=aliased_index,
            alias=base_name,
        )

    if alias := _extra_alias(job):
        AddAliasTask.objects.create(
            job=job, index=new_index, alias=alias
        )

        for aliased_index in indices_with_alias(server, alias, base_name):
            RemoveAliasTask.objects.create(
                job=job, index=aliased_index, alias=alias
            )


def _server_for_job(job: IndexJob):
    server_name = server_for_corpus(job.corpus.name)
    server = Server.objects.get(name=server_name)
    return server


def _index_and_base_name_for_job(job: IndexJob, prod: bool, create_new: bool) -> Tuple[Index, str]:
    corpus = job.corpus
    server = _server_for_job(job)
    client = elasticsearch(corpus.name)
    base_name = _index_base_name(server, corpus)

    if prod:
        if create_new:
            next_version = next_version_number(client, base_name)
            versioned_name = f'{base_name}-{next_version}'
        else:
            versioned_name = get_current_index_name(
                corpus.configuration, client
            )

        index, _ = Index.objects.get_or_create(
            server=server, name=versioned_name
        )
    else:
        index, _ = Index.objects.get_or_create(
            server=server, name=base_name
        )

    return index, base_name


def _index_base_name(server: Server, corpus: Corpus) -> str:
    if corpus.configuration.es_index:
        return corpus.configuration.es_index

    prefix = server.configuration.get('index_prefix', None)
    name = corpus.name if corpus.has_python_definition else f'custom_{corpus.pk}'
    return f'{prefix}-{name}' if prefix else name


def _extra_alias(job: IndexJob) -> Optional[str]:
    if alias := job.corpus.configuration.es_alias:
        return alias


@transaction.atomic
def create_alias_job(corpus: Corpus, clean=False) -> IndexJob:
    '''
    Create a job to move the alias of a corpus to the index with the highest version
    '''

    job = IndexJob.objects.create(corpus=corpus)

    corpus_name = corpus.name
    update_server_table_from_settings()
    server = Server.objects.get(name=server_for_corpus(corpus_name))
    base_name = _index_base_name(server, corpus)
    client = elasticsearch(corpus_name)

    indices = indices_with_base_name(client, base_name)
    if not len(indices):
        raise Exception('No matching index found')

    highest_version = highest_version_in_result(indices, base_name)
    latest_index, _ = Index.objects.get_or_create(
        server=server,
        name=f'{base_name}-{highest_version}'
    )

    _add_alias_rollover_tasks(job, server, base_name, latest_index)

    if clean:
        for index_name in indices:
            is_highest_version = version_from_name(index_name, base_name) == highest_version

            if not is_highest_version:
                index, _ = Index.objects.get_or_create(server=server, name=index_name)
                DeleteIndexTask.objects.create(job=job, index=index)

    return job
