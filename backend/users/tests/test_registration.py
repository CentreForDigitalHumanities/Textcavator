from django.core import mail
import random
import re
import string

from django.core.cache import cache
from django.urls import reverse
from allauth.account.models import EmailAddress
from rest_framework import status


def test_register_verification(client, db, django_user_model):
    creds = {
        'username': 'ThomasCromwell',
        'password1': 'annaregina',
        'password2': 'annaregina',
        'email': 'thomas@wolfhall.com'
    }
    response = client.post('/users/registration/', creds)
    assert response

    # Check if user was registered
    db_user = django_user_model.objects.get(
        username=creds['username'])
    assert db_user

    # Check if basic group was assigned
    assert db_user.groups.get(name='basic')

    # Check if registration mail was sent
    box = mail.outbox
    assert len(box) == 1
    verify_mail = box[0]
    assert verify_mail.to[0] == creds['email']

    key = re.search(r'confirm-email\/(.+)\/',
                    verify_mail.body).group(1)
    assert key

    # Check key information
    key_info = client.post('/users/registration/key-info/', {'key': key})
    assert key_info.status_code == 200
    assert key_info.data.get('username') == creds.get('username')

    # Check verification
    verify_response = client.post(
        '/users/registration/verify-email/', {'key': key})
    assert verify_response.status_code == 200

    # Check if email address was verified
    allauth_email = EmailAddress.objects.get(user=db_user)
    assert allauth_email.email == creds.get('email')
    assert allauth_email.verified is True
    assert allauth_email.primary is True


def test_register_throttling(client, settings, db):
    """
    Test that the ThrottledRegisterView returns a 429 error
    after exceeding the allowed number of registration attempts.
    """
    # Check conftest.py throttle rate settings are applied
    registration_rate = settings.REST_FRAMEWORK.get(
        'DEFAULT_THROTTLE_RATES', {}).get('registration')
    assert registration_rate == '2/minute', \
        f"Expected registration throttle rate to be '2/minute', but got '{registration_rate}'."

    register_url = reverse('rest_register')

    def generate_user_data():
        """Generate unique user data."""
        random_str = ''.join(random.choices(string.digits, k=4))
        return {
            'username': f'testuser{random_str}',
            'password1': 'Testpass123!',
            'password2': 'Testpass123!',
            'email': f'testuser{random_str}@example.com'
        }

    # Test that the view returns 429 after 3 requests
    registration_rate = int(registration_rate.split('/')[0])
    for i in range(1, registration_rate + 2):
        user_data = generate_user_data()
        response = client.post(register_url, user_data, format='json')
        print(f"Request {i} status: {response.status_code}")

        if i == registration_rate + 1:
            assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS, \
                f"Expected 429, got {response.status_code}"
            response_data = response.json()
            assert 'detail' in response_data, "Response does not contain 'detail' key"
