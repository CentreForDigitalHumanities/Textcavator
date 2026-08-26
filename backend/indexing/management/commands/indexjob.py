from typing import Callable
from csv import DictWriter
from sys import stdout

from django.core.management import BaseCommand

from indexing.constants import TaskStatus
from indexing.models import IndexJob
from indexing.command_utils import run_job, add_async_argument
from indexing.stop_job import is_stoppable, mark_tasks_stopped


class Command(BaseCommand):
    help = '''
    Create, populate or clear elasticsearch indices for corpora.
    '''

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            help='Type of action',
        )

        parser_list = subparsers.add_parser(
            'list',
            help='List all index jobs',
            description='Display a table of all index jobs',
        )
        parser_list.set_defaults(handler=self.list),

        parser_show = subparsers.add_parser(
            'show',
            help='Show information about a job',
            description='Show details about a job.'
        )
        parser_show.add_argument(
            'id',
            type=int,
            help='ID of the job to display',
        )
        parser_show.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Show detailed task data',
        )
        parser_show.set_defaults(handler=self.show),

        parser_start = subparsers.add_parser(
            'start',
            help='Start a job',
        )
        parser_start.add_argument(
            'id',
            type=int,
            help='ID of the job to start',
        )
        add_async_argument(parser_start)
        parser_start.set_defaults(handler=self.start)

        parser_stop = subparsers.add_parser(
            'stop',
            help='Stop an job that is currently running',
        )
        parser_stop.add_argument(
            'id',
            type=int,
            help='ID of the job to cancel',
        )
        parser_stop.set_defaults(handler=self.stop)


    def handle(self, handler: Callable, **options):
        handler(**options)


    def list(self, **options):
        jobs = IndexJob.objects.all()

        writer = DictWriter(
            fieldnames=['id', 'corpus', 'created', 'status'],
            f=stdout,
            delimiter='\t',
        )
        writer.writeheader()
        for job in jobs:
            writer.writerow({
                'id': job.id,
                'corpus': job.corpus,
                'created': job.created,
                'status': job.status()
            })

    def show(self, id: int, verbose=False, **options):
        job = IndexJob.objects.get(id=id)
        print('JOB #', job.id, sep='')
        print('CORPUS:', job.corpus)
        print('CREATED ON:', job.created)
        print('STATUS:', job.status())

        print('TASKS:')
        for task in job.tasks():
            print(f'- {task} [{task.status}]')

            if verbose:
                print('    * type:', task.__class__.__name__)
                field_values = (
                    (field.name, getattr(task, field.name))
                    for field in task._meta.fields
                )
                for parameter, value in field_values:
                    print(f'    * {parameter}: {value}')


    def start(self, id: int, run_async=False, **options):
        job = IndexJob.objects.get(id=id)

        if job.status() != TaskStatus.CREATED:
            print(
                f'Job {job.id} cannot be started: current status is {job.status()}'
            )
            return

        print(f'Starting job: {job.id}')
        run_job(job, run_async)

    def stop(self, id: int, **options):
        job = IndexJob.objects.get(id=id)

        if is_stoppable(job):
            mark_tasks_stopped(job)
            print(f'Job {job.id} stopped')
        else:
            self.stdout.write(self.style.WARNING(
                f'Job {job.id} is not running; no action taken.'
            ))
