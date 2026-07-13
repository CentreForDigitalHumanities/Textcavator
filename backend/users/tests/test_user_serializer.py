from users.models import CustomUser
from users.serializers import CustomUserDetailsSerializer
from unittest.mock import ANY

def test_user_serializer(auth_client, user_credentials):
    details = auth_client.get('/users/user/')
    assert details.status_code == 200
    assert details.data == {
        'id': ANY,
        'name': user_credentials['username'],
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
        'name': admin_credentials['username'],
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



def test_saml_user_serializer(saml_user):
    serializer = CustomUserDetailsSerializer(instance=saml_user)
    assert serializer.data == {
        'id': ANY,
        'name': 'test1',
        'email': 'test1@example.com',
        'download_limit': 10000,
        'is_admin': False,
        'saml': True,
        'profile': {
            'enable_search_history': True,
            'can_edit_corpora': False,
        },
    }
