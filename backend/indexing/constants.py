from django.db.models import TextChoices

class TaskStatus(TextChoices):
    CREATED = 'created'
    'Task is created, but not scheduled'

    QUEUED = 'queued'
    'Task has not started, but its job has been started'

    WORKING = 'working'
    'Task is currently running'

    DONE = 'done'
    'Task completed successfully'

    ERROR = 'error'
    'Task ran into an error'

    ABORTED = 'aborted'
    'Task was started, then aborted by a user'

    CANCELLED = 'cancelled'
    'Task was cancelled (because a task up-chain was aborted or failed)'
