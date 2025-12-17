import os
from datetime import datetime

import django.contrib.auth.hashers as hashers
import pytest
from addcorpus.models import Corpus
from allauth.account.models import EmailAddress
from api.models import Query
from django.contrib.auth.models import Group
from download.models import Download
from ianalyzer.flask_data_transfer import *
from users.models import CustomUser

_here = os.path.abspath(os.path.dirname(__file__))
flask_test_data_dir = os.path.join(_here, 'flask_test_data')


def test_legacy_data_import():
    user_data = import_table_data(flask_test_data_dir, 'user')

    assert len(user_data) == 4

    user = user_data[0]
    expected_user = {
        'id': '1',
        'username': 'admin',
        'password': 'password',
        'email': 'admin@textcavator.nl',
        'active': '1',
        'authenticated': '1',
        'download_limit': '10000',
        'role_id': '2',
        'saml': '0'
    }

    for key in expected_user:
        if key == 'password':
            encoded = adapt_password_encoding(user['password'])
            assert hashers.check_password(expected_user['password'], encoded)
        else:
            assert user[key] == expected_user[key]


def test_roles_import():
    role_data = import_table_data(flask_test_data_dir, 'role')

    assert len(role_data) == 2

    role = role_data[0]
    expected_role = {
        'id': '1',
        'name': 'basic',
        'description': 'corpora for public access'
    }

    assert role == expected_role


def test_save_groups(db):
    import_and_save_table(flask_test_data_dir, 'role', save_flask_group)

    groups = Group.objects.all()
    assert len(groups) == 2


def test_save_legacy_user(db):
    import_and_save_table(flask_test_data_dir, 'role', save_flask_group)
    import_and_save_table(flask_test_data_dir, 'user', save_flask_user)

    users = CustomUser.objects.all()

    assert len(users) == 4
    admin = CustomUser.objects.get(username='admin')
    assert admin.username == 'admin'
    assert admin.email == 'admin@textcavator.nl'
    assert admin.is_superuser
    assert admin.is_staff
    assert not admin.saml
    assert list(admin.groups.all()) == [Group.objects.get(
        name='basic'), Group.objects.get(name='admin')]

    allauth_email = EmailAddress.objects.get(user=admin)
    assert allauth_email.email == admin.email
    assert allauth_email.verified

    saml = users[1]
    assert not saml.is_superuser
    assert saml.saml

def test_save_corpora(db):
    import_and_save_table(flask_test_data_dir, 'role', save_flask_group)
    import_and_save_table(flask_test_data_dir, 'corpus', save_flask_corpus)
    import_and_save_table(flask_test_data_dir,
                          'corpora_roles', save_flask_corpus_role)

    corpora = Corpus.objects.all()
    assert len(corpora) == 13

    corpus = Corpus.objects.get(id='13')
    assert corpus.name == 'parliament-ireland'
    assert set(corpus.groups.all()) == set(Group.objects.all())


def dates_match(datetime1, datetime2):
    '''To avoid timezone issues, just check the dates to compare to datetime objects'''
    return datetime1.date() == datetime2.date()


@pytest.mark.filterwarnings(
    'ignore:DateTimeField .* received a naive datetime (.*) while time zone support is active'
)
def test_save_queries(db):
    import_and_save_all_data(flask_test_data_dir)

    queries = Query.objects.all()
    assert len(queries) == 11

    query = Query.objects.get(id='507')

    assert query.query_json == {
        "sort": [{"date": "desc"}],
        "query": {"bool": {"must": {"match_all": {}}, "filter": []}}
    }


    assert dates_match(query.started,
                       datetime(year=2022, month=12, day=7, hour=14, minute=18, second=6))
    assert query.completed is None
    assert query.total_results == 7915
    assert query.aborted is False
    assert query.transferred == 0
    assert query.user == CustomUser.objects.get(username='admin')
    assert query.corpus == Corpus.objects.get(name='parliament-ireland')


@pytest.mark.filterwarnings(
    'ignore:DateTimeField .* received a naive datetime (.*) while time zone support is active'
)
def test_save_downloads(db):
    import_and_save_all_data(flask_test_data_dir)

    downloads = Download.objects.all()
    assert len(downloads) == 10

    download = Download.objects.get(id='49')
    assert dates_match(download.started,
                       datetime(year=2022, month=11, day=21, hour=10, minute=59, second=26))
    assert dates_match(download.completed,
                       datetime(year=2022, month=11, day=21, hour=10, minute=59, second=27))
    assert download.corpus == Corpus.objects.get(name='parliament-uk')
    assert download.user == CustomUser.objects.get(id='1')
    assert download.parameters == {
        "corpus": "parliament-uk",
        "es_query": {
            "query": {"bool": {"must": {"match_all": {}}, "filter": []}},
            "sort": [{"date": "desc"}]},
        "fields": ["date", "speech", "id", "sequence", "speaker"],
        "route": "/search/parliament-uk"
    }

    _, filename = os.path.split(download.filename)
    assert filename == 'parliament-uk.csv'


def test_no_data_to_import(db):
    '''Assert that a missing directory or missing files will raise a warning
    but not crash'''
    with pytest.warns(Warning, match='skipping database migration'):
        import_and_save_all_data('./nonexistent-directory')

    with pytest.warns(Warning, match='skipping table migration'):
        import_table_data(flask_test_data_dir, 'nonexistent_table.txt')
