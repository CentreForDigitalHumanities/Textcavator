'''
Functionality to run indexing tasks too straightforward to warrant a separate module
'''

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from indexing.models import (
        DeleteIndexTask, RemoveAliasTask, AddAliasTask, UpdateSettingsTask,
    )


def add_alias(task: 'AddAliasTask'):
    '''
    Add an alias to an Elasticsearch index, as defined by an AddAliasTask
    '''
    client = task.client()
    client.indices.put_alias(
        index=task.index.name,
        name=task.alias
    )


def remove_alias(task: 'RemoveAliasTask'):
    '''
    Remove an alias from an Elasticsearch index, as defined by a RemoveAliasTask
    '''
    client = task.client()
    client.indices.delete_alias(
        index=task.index.name,
        name=task.alias
    )


def delete_index(task: 'DeleteIndexTask'):
    '''
    Delete an Elasticsearch index, as defined by a DeleteIndexTask
    '''
    client = task.client()
    client.indices.delete(
        index=task.index.name,
    )


def update_index_settings(task: 'UpdateSettingsTask'):
    client = task.client()
    client.indices.put_settings(
        settings=task.settings,
        index=task.index.name,
        allow_no_indices=False,
    )




