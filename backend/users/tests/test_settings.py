def test_username_update(auth_user, auth_client):
    response = auth_client.patch('/users/user/',
        {'username': 'new_name'},
        content_type='application/json'
    )
    assert response.status_code == 200

    auth_user.refresh_from_db()
    assert auth_user.username == 'new_name'

def test_user_profile_update(auth_client):
    route = '/users/user/'
    details = lambda: auth_client.get(route)
    search_history_enabled = lambda: details().data.get('profile').get('enable_search_history')

    assert search_history_enabled()

    response = auth_client.patch(route, {'profile': {'enable_search_history': False}}, content_type='application/json')
    assert response.status_code == 200

    assert not search_history_enabled()


def test_readonly_field_update(auth_client):
    '''
    Test that is_admin is readonly
    '''

    route = '/users/user/'
    details = lambda: auth_client.get(route)
    is_admin = lambda: details().data.get('is_admin')

    assert not is_admin()
    response = auth_client.patch(route, {'is_admin': True}, content_type='application/json')
    assert not is_admin()


def test_saml_username_is_readonly(saml_user, saml_client):
    response = saml_client.patch('/users/user/',
        {'username': 'new_name'},
        content_type='application/json'
    )

    saml_user.refresh_from_db()
    assert saml_user.username != 'new_name'
