from django.core.management.base import BaseCommand
from addcorpus.models import Corpus
from bow.create_index_job import create_bow_index_job
from indexing.command_utils import run_job, add_create_only_argument, add_async_argument


class Command(BaseCommand):
    help = '''
    Load all python corpus definitions (configured in settings)
    into the database.

    This command will add any newly added corpora to the database,
    and update any existing corpora.

    If a corpus is removed from settings or cannot be successfully
    loaded, it will not be removed from the database, to prevent data
    loss.
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            'corpus',
            help='''Sets which corpus should be indexed. This should match the "name"
                field in the database. For Python corpora, this field is based on the
                name in settings.py''',
        )

        add_create_only_argument(parser)
        add_async_argument(parser, 'Cannot be used in combination with --create-only.')


    def handle(self, corpus, create_only=False, run_async=False, **kwargs):
        corpus_obj = Corpus.objects.get(name=corpus)
        # TODO: validate corpus state

        job = create_bow_index_job(corpus_obj)
        print(f'Created IndexJob #{job.pk}')

        if not create_only:
            run_job(job, run_async)
