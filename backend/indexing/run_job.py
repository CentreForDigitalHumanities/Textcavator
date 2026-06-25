'''
Functionality to run an IndexJob
'''

import logging
from typing import Callable, Type, Dict
import celery
from celery.result import AsyncResult
from celery.contrib.abortable import AbortableTask

from es.client import elasticsearch
from indexing.models import (
    IndexJob, IndexTask, TaskStatus, CreateIndexTask, PopulateIndexTask,
    UpdateSettingsTask, RemoveAliasTask, AddAliasTask, DeleteIndexTask, UpdateIndexTask
)
from analysis.models import CreateTokenIndexTask, PopulateTokenIndexTask
from analysis.run_index_tasks import create_token_index, populate_token_index
from indexing.run_populate_task import populate
from indexing.run_create_task import create
from indexing.run_management_tasks import (
    update_index_settings, remove_alias, add_alias, delete_index
)
from indexing.run_update_task import run_update_task
from ianalyzer.celery_utils import warn_if_no_worker
from indexing.stop_job import mark_tasks_stopped, TaskAborted, raise_if_aborted


logger = logging.getLogger('indexing')

TASK_HANDLERS: Dict[Type[IndexTask], Callable[[IndexTask], None]] = {
    CreateIndexTask: create,
    PopulateIndexTask: populate,
    UpdateIndexTask: run_update_task,
    UpdateSettingsTask: update_index_settings,
    RemoveAliasTask: remove_alias,
    AddAliasTask: add_alias,
    DeleteIndexTask: delete_index,
    CreateTokenIndexTask: create_token_index,
    PopulateTokenIndexTask: populate_token_index
}


@celery.shared_task()
def run_task(task: IndexTask) -> None:
    '''Run an IndexTask'''

    task_id = f'{task.__class__.__name__} #{task.pk}' # e.g. "CreateIndexTask #1"

    if task.is_aborted():
        logger.warning(f'{task_id} cancelled')
        return

    logger.info(f'Running {task_id}: {task}')

    task.status = TaskStatus.WORKING
    task.save()

    try:
        task.client().cluster.health(wait_for_status='yellow')
        handler = TASK_HANDLERS[task.__class__]
        handler(task)
    except TaskAborted:
        # exception raised by the handler if the task is aborted mid-execution
        logger.warning(f'{task_id} aborted')
        return
    except Exception as e:
        logger.exception(f'{task_id} failed!')
        task.status = TaskStatus.ERROR
        task.save()
        raise

    task.status = TaskStatus.DONE
    task.save()
    logger.info(f'{task_id} completed')


@celery.shared_task()
def handle_job_error(request, exc, traceback, job: IndexJob):
    mark_tasks_stopped(job)


@celery.shared_task()
def start_job(job: IndexJob) -> None:
    _log_job_started(job)

    try:
        _validate_job_start(job)
    except Exception as e:
        logger.warning(f'Index job {job.pk} cancelled: validation failed', exc_info=True)
        mark_tasks_stopped(job)
        return

    for task in job.tasks():
        task.status = TaskStatus.QUEUED
        task.save()


def job_chain(job: IndexJob) -> celery.chain:
    signatures = [start_job.si(job)] + [run_task.si(task) for task in job.tasks()]
    return celery.chain(signatures).on_error(handle_job_error.s(job))


def perform_indexing(job: IndexJob):
    '''
    Run an IndexJob by running all related tasks.
    '''

    chain = job_chain(job)
    return chain.apply()


def perform_indexing_async(job: IndexJob) -> AsyncResult:
    '''
    Run an IndexJob asynchronously (through celery)
    '''

    warn_if_no_worker()
    chain = job_chain(job)
    return chain.apply_async()


def _validate_job_start(job: IndexJob):
    '''Validation that should be run before starting an IndexJob'''
    assert job.status() == TaskStatus.CREATED
    job.corpus.validate_ready_to_index()


def _log_job_started(job: IndexJob):
    corpus_name = job.corpus.name

    logger.info(f'Started index job: {job}')

    # Create and populate the ES index
    client = elasticsearch(corpus_name)
    logger.info('max_retries: {}'.format(vars(client).get('_max_retries')))
    logger.info('retry on timeout: {}'.format(
        vars(client).get('_retry_on_timeout'))
    )
