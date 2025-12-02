from datetime import datetime
import os
from io import StringIO
import pytest
from django.core.management import call_command

from addcorpus.models import Corpus
from download.models import Download

def test_delete_old_downloads_records(
    db, basic_mock_corpus, auth_user, csv_directory, tmp_path_factory,
    monkeypatch,
):
    '''
    Test deleting old download records using the command line.

    Creates a "legacy" record where the file has a different directory + filename than
    the application would currently generate.
    '''
    corpus = Corpus.objects.get(name=basic_mock_corpus)
    path = tmp_path_factory.mktemp('old_downloads') / 'mydownload.csv'

    with open(path, 'w') as f:
        f.write('Bla bla bla')

    old_record = Download.objects.create(
        download_type='search_results',
        corpus=corpus,
        user=auth_user,
        parameters={'foo': 'bar'},
        filename=path,
    )
    # date is overridden in creation due to auto_now_add, set it now
    old_record.started = datetime(year=1800, month=1, day=1, hour=0, minute=0)
    old_record.completed = datetime(year=1800, month=1, day=1, hour=0, minute=1)
    old_record.save()

    assert os.path.exists(old_record.filename)

    monkeypatch.setattr('sys.stdin', StringIO('y\n'))
    call_command('delete_old_downloads')


    with pytest.raises(Download.DoesNotExist):
        old_record.refresh_from_db()

    assert not os.path.exists(old_record.filename)


def test_delete_old_downloads_files(
    db, csv_directory, monkeypatch,
):
    '''
    Test deleting orphan files in the download folder using the command line.
    '''
    path = os.path.join(csv_directory, 'mydownload.csv')

    with open(path, 'w') as f:
        f.write('Bla bla bla')

    assert os.path.exists(path)

    monkeypatch.setattr('sys.stdin', StringIO('y\n'))
    call_command('delete_old_downloads')

    assert not os.path.exists(path)
