from users.models import CustomUser
from users.serializers import CustomUserDetailsSerializer
from unittest.mock import ANY

def test_user_serializer(auth_client,
                         user_credentials):
    details = auth_client.get('/users/user/')
    assert details.status_code == 200
    assert details.data == {
        'id': ANY,
        'username': user_credentials['username'],
        'email': user_credentials['email'],
        'download_limit': 10000,
        'is_admin': False,
        'saml': False,
        'profile': {
            'enable_search_history': True,
            'can_edit_corpora': False,
        },
    }


def test_admin_serializer(admin_client, admin_credentials):
    details = admin_client.get('/users/user/')
    assert details.status_code == 200
    assert details.data == {
        'id': ANY,
        'username': admin_credentials['username'],
        'email': admin_credentials['email'],
        'download_limit': 1000000,
        'is_admin': True,
        'saml': False,
        'profile': {
            'enable_search_history': True,
            'can_edit_corpora': True,
        },
    }

def test_user_updates(auth_client):
    route = '/users/user/'
    details = lambda: auth_client.get(route)
    search_history_enabled = lambda: details().data.get('profile').get('enable_search_history')

    assert search_history_enabled()

    response = auth_client.patch(route, {'profile': {'enable_search_history': False}}, content_type='application/json')
    assert response.status_code == 200

    assert not search_history_enabled()

def test_readonly_fields(auth_client):
    '''
    Test that is_admin is readonly
    '''

    route = '/users/user/'
    details = lambda: auth_client.get(route)
    is_admin = lambda: details().data.get('is_admin')

    assert not is_admin()
    response = auth_client.patch(route, {'is_admin': True}, content_type='application/json')
    assert not is_admin()


def test_saml_user_serializer(db):
    user = CustomUser(
        username='_',
        saml_username='test1',
        email='test1@example.com',
        saml=True,
    )
    user.set_unusable_password()
    user.save()

    serializer = CustomUserDetailsSerializer(instance=user)
    assert serializer.data['saml'] == True
    assert serializer.data['username'] == 'test1'
