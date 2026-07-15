import django.contrib.auth.models as django_auth_models
from django.db import models


DEFAULT_DOWNLOAD_LIMIT = 10000
PUBLIC_GROUP_NAME = 'basic'

class CustomUser(django_auth_models.AbstractUser):
    saml = models.BooleanField(blank=True, null=True, default=False)
    download_limit = models.IntegerField(
        help_text='Maximum documents that this user can download per query',
        default=DEFAULT_DOWNLOAD_LIMIT)

    saml_username = models.CharField(
        max_length=256,
        help_text='Username for SAML login',
        unique=True,
        blank=True,
        null=True,
    )

    def __str__(self):
        if self.saml_username:
            return f'{self.saml_username} [saml]'
        return super().__str__()

    def get_short_name(self):
        return self.saml_username or self.username


class AnoymousProfile(object):
    enable_search_history = False


class CustomAnonymousUser(django_auth_models.AnonymousUser):
    ''' extend AnonymousUser class with has_access method
        return True for any corpus assigned to the `basic` group
    '''
    profile = AnoymousProfile()


django_auth_models.AnonymousUser = CustomAnonymousUser


class UserProfile(models.Model):
    ''' User information that is not relevant to authentication.
    E.g. settings, preferences, optional personal information.
    '''

    user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    enable_search_history = models.BooleanField(
        help_text='Whether to save the search history of this user',
        default=True,
    )

    can_edit_corpora = models.BooleanField(
        default=False,
        help_text='Whether the user is allowed to edit corpora',
    )

    def __str__(self):
        return f'Profile of {self.user}'

