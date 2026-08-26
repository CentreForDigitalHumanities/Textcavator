from typing import TYPE_CHECKING
from indexing.constants import TaskStatus

if TYPE_CHECKING:
    from indexing.models import IndexJob, IndexTask


def is_stoppable(job: 'IndexJob'):
    return job.status() in [TaskStatus.QUEUED, TaskStatus.WORKING]

def mark_tasks_stopped(job: 'IndexJob'):
    '''
    Mark open tasks as aborted and queued tasks as cancelled.

    Note that this just updates the database status; the task handler must avoid
    execution.
    '''
    for task_set in job.task_query_sets():
        task_set.filter(status=TaskStatus.CREATED).update(status=TaskStatus.CANCELLED)
        task_set.filter(status=TaskStatus.QUEUED).update(status=TaskStatus.CANCELLED)
        task_set.filter(status=TaskStatus.WORKING).update(status=TaskStatus.ABORTED)

class TaskAborted(Exception):
    pass

def raise_if_aborted(task: 'IndexTask'):
    '''
    Raise an exception is the index task is aborted.

    This can be used to interrupt execution in a task handler. Note that the
    `run_task` wrapper will check the task status at the start; adding checks
    is useful for long-running tasks.
    '''
    task.refresh_from_db()
    if task.is_aborted():
        raise TaskAborted
