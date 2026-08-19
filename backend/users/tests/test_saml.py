import pytest
from users.models import CustomUser
from users.saml import CustomSaml2Backend

@pytest.fixture
def saml_backend(db, settings):
    settings.SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'saml_username'
    backend = CustomSaml2Backend()
    return backend


def authenticate(saml_backend: CustomSaml2Backend):
    return saml_backend.authenticate(
        request=None,
        session_info={
            'ava': {
                'uuShortID': ['test1'],
                'mail': ['test2@examle.com'],
            },
            'issuer': '',
        },
        attribute_mapping={
            'uuShortID': ('saml_username',),
            'mail': ('email',),
        }
    )


def test_saml_authenticate_new_user(db, saml_backend):
    user = authenticate(saml_backend)
    assert user.saml
    assert user.saml_username == 'test1'


def test_saml_authenticate_existing_user(saml_backend):
    existing = CustomUser(
        username='placeholder',
        email='test1@example.com',
        saml_username='test1',
        saml=True,
    )
    existing.set_unusable_password()
    existing.save()

    user = authenticate(saml_backend)
    assert user == existing


def test_saml_user_matches_regular_account(saml_backend):
    existing = CustomUser(
        username='test1',
        email='test1@example.com',
    )
    existing.set_password('secret')
    existing.save()

    user = authenticate(saml_backend)
    assert user
    assert user != existing

