'''
Functionality to run indexing tasks too straightforward to warrant a separate module
'''

from time import sleep
from indexing.models import (
    DeleteIndexTask, RemoveAliasTask, AddAliasTask, UpdateSettingsTask, ReindexTask
)
from indexing.stop_job import TaskAborted


def add_alias(task: AddAliasTask):
    '''
    Add an alias to an Elasticsearch index, as defined by an AddAliasTask
    '''
    client = task.client()
    client.indices.put_alias(
        index=task.index.name,
        name=task.alias
    )


def remove_alias(task: RemoveAliasTask):
    '''
    Remove an alias from an Elasticsearch index, as defined by a RemoveAliasTask
    '''
    client = task.client()
    client.indices.delete_alias(
        index=task.index.name,
        name=task.alias
    )


def delete_index(task: DeleteIndexTask):
    '''
    Delete an Elasticsearch index, as defined by a DeleteIndexTask
    '''
    client = task.client()
    client.indices.delete(
        index=task.index.name,
    )


def update_index_settings(task: UpdateSettingsTask):
    client = task.client()
    client.indices.put_settings(
        settings=task.settings,
        index=task.index.name,
        allow_no_indices=False,
    )


def reindex(task: ReindexTask):
    client = task.client()
    response = client.reindex(
        source={'index': task.source_index.name},
        dest={'index': task.index.name},
        wait_for_completion=False,
        timeout='10s',
    )
    # if timeout expired, poll task
    if 'task' in response.body:
        task_id = response.body['task']
        complete = False
        while not complete:
            sleep(60)
            response = client.tasks.get(task_id=task_id)

            # break loop if completed
            if response.body.get('completed'):
                complete = True

            # cancel task if aborted
            task.refresh_from_db()
            if task.is_aborted():
                client.tasks.cancel(task_id=task_id)
                raise TaskAborted()
