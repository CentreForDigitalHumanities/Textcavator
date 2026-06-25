from django.db import models
from elasticsearch import Elasticsearch
from typing import List, Optional
from itertools import chain
from django.contrib import admin

from es.client import elasticsearch
from addcorpus.models import Corpus
from es.models import Index


class TaskStatus(models.TextChoices):
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


class IndexJob(models.Model):
    '''
    Represents a collection of index-related tasks that are carried out together.
    '''

    corpus = models.ForeignKey(
        to=Corpus,
        on_delete=models.CASCADE,
        help_text='corpus for which the job is created; tasks may use the corpus '
            'to determine index configuration or extract documents',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text='time when the job was created',
    )


    def tasks(self) -> List['IndexTask']:
        '''
        A list of all tasks that belong to this job, in order of execution.

        Tasks are ordered by type. The order of types is:
        - `CreateIndexTask`
        - `PopulateIndexTask`
        - `UpdateIndexTask`
        - `UpdateSettingsTask`
        - `RemoveAliasTask`
        - `AddAliasTask`
        - `DeleteIndexTask`
        '''
        return list(chain(*self.task_query_sets()))


    def task_query_sets(self) -> List[models.QuerySet['IndexTask']]:
        '''
        For each task type, the queryset of tasks that belong to this job.

        Can be used to run bulk updates on related tasks.
        '''
        return [
            self.createindextasks.all(),
            self.populateindextasks.all(),
            self.updateindextasks.all(),
            self.updatesettingstasks.all(),
            self.createtokenindextasks.all(),
            self.populatetokenindextasks.all(),
            self.removealiastasks.all(),
            self.addaliastasks.all(),
            self.deleteindextasks.all(),
        ]


    def __str__(self):
        return f'{self.corpus} ({self.created})'


    @admin.display()
    def status(self) -> Optional[TaskStatus]:
        '''Aggregate status of related tasks'''
        statuses = set(task.status for task in self.tasks())
        if len(statuses) == 1:
            return statuses.pop()
        if TaskStatus.ERROR in statuses:
            return TaskStatus.ERROR
        if TaskStatus.WORKING in statuses:
            return TaskStatus.WORKING
        if TaskStatus.ABORTED in statuses:
            return TaskStatus.ABORTED



class IndexTask(models.Model):
    '''
    Abstract model for index-related tasks.
    '''

    class Meta:
        abstract = True

    job = models.ForeignKey(
        to=IndexJob,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        help_text='job in which this task is run',
    )
    index = models.ForeignKey(
        to=Index,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        help_text='index on which this task is applied',
    )
    status = models.CharField(
        max_length=16,
        choices=TaskStatus.choices,
        default=TaskStatus.CREATED,
        help_text='execution status of this task',
    )

    @property
    def corpus(self) -> Corpus:
        return self.job.corpus

    def client(self) -> Elasticsearch:
        return elasticsearch(self.corpus.name)

    def is_aborted(self) -> bool:
        self.refresh_from_db()
        return self.status in [TaskStatus.CANCELLED, TaskStatus.ABORTED]


class CreateIndexTask(IndexTask):
    '''
    Create a new index based on corpus settings.
    '''

    production_settings = models.BooleanField(
        default=False,
        help_text='configure index settings for a production environment',
    )
    delete_existing = models.BooleanField(
        default=False,
        help_text='if an index by this name already exists, delete it, instead of '
            'raising an exception'
    )

    def __str__(self):
        return f'create {self.index} based on {self.corpus}'

class PopulateIndexTask(IndexTask):
    '''
    Extract documents from a corpus and add them to the index.
    '''

    document_min_date = models.DateField(
        blank=True,
        null=True,
        help_text='minimum date on which to filter documents'
    )
    document_max_date = models.DateField(
        blank=True,
        null=True,
        help_text='maximum date on which to filter documents'
    )

    def __str__(self):
        return f'populate {self.index} based on {self.corpus}'


class UpdateIndexTask(IndexTask):
    '''
    Run an update script; usually to add/change field values in existing documents.

    Only available for corpora with a Python definition (which must also include a method
    that defines such a script).
    '''

    document_min_date = models.DateField(
        blank=True,
        null=True,
        help_text='minimum date on which to filter documents'
    )
    document_max_date = models.DateField(
        blank=True,
        null=True,
        help_text='maximum date on which to filter documents'
    )

    def __str__(self):
        return f'update {self.index} based on {self.corpus}'



class UpdateSettingsTask(IndexTask):
    '''
    Push new settings to an index
    '''

    settings = models.JSONField(
        blank=True,
        default=dict,
        help_text='settings to push',
    )

    def __str__(self):
        return f'update settings of {self.index}'


class RemoveAliasTask(IndexTask):
    '''
    Remove an alias from an index
    '''
    alias = models.CharField(
        max_length=128,
        help_text='alias to remove'
    )

    def __str__(self):
        return f'remove alias {self.alias} from {self.index}'


class AddAliasTask(IndexTask):
    '''
    Add an alias to an index
    '''
    alias = models.CharField(
        max_length=128,
        help_text='alias to assign'
    )

    def __str__(self):
        return f'add alias {self.alias} to {self.index}'


class DeleteIndexTask(IndexTask):
    '''
    Delete an index.
    '''

    def __str__(self):
        return f'delete {self.index}'
