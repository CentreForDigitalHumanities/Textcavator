from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
import os

from download.models import Download, csv_directory

class Command(BaseCommand):
    help = '''
    Delete all downloads older than 90 days and remove all files in the downloads folder
    that are not related to a download object (typically from older Textcavator versions).

    This can be used to reduce storage in the downloads folder.
    '''

    def handle(self, *args, **kwargs):
        cutoff = datetime.now() - timedelta(days=90)
        old_downloads = Download.objects.filter(started__lte=cutoff)

        print('Download records older than 90 days:', old_downloads.count())

        dir = os.path.abspath(csv_directory())
        all_files = os.listdir(dir)
        all_paths = set(os.path.join(dir, filename) for filename in all_files)

        download_paths = set(
            os.path.abspath(d.filename)
            for d in Download.objects.filter(filename__isnull=False)
        )

        orphan_files = [
            path for path in all_paths
            if not any(path == download_path for download_path in download_paths)
        ]

        print('Files without a download record:', len(orphan_files))

        print('These records and files will be deleted. Continue? (y/N)')
        response = input().lower()

        if response == 'y':
            print('Removing downloads records...')
            old_downloads.delete()

            print('Removing orphan files...')
            for path in orphan_files:
                try:
                    os.remove(path)
                except Exception as e:
                    print(self.style.WARNING(f'Could not remove {path}: {e}'))
            print(self.style.SUCCESS('Finished'))
        else:
            print('No action taken.')

