import os
from django.core import mail
import pytest

from download.models import Download
from addcorpus.models import Corpus
from download.mail import send_csv_email

@pytest.fixture()
def finished_download(admin_user, mock_corpus, csv_directory):
    corpus = Corpus.objects.get(name=mock_corpus)
    download = Download.objects.create(
        download_type='search_results',
        corpus=corpus,
        user=admin_user,
        parameters = {}
    )

    filename = 'test.csv'
    with open(os.path.join(csv_directory, filename), 'w') as csv_file:
        csv_file.write('test')

    download.complete(filename)

    return download

def test_download_mail(admin_user, admin_client, finished_download):
    send_csv_email(admin_user.email, admin_user.username, finished_download.id)

    csv_mail = mail.outbox[0]
    assert csv_mail
    assert csv_mail.subject == 'Textcavator CSV download'
    assert csv_mail.to == [admin_user.email]
