import os
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings
import logging

from download.models import Download

logger = logging.getLogger()

def download_url(download_id):
    return settings.BASE_URL + reverse('download-csv', kwargs={'id': download_id})

def send_csv_email(user_email, username, download_id):
    '''
    Send an email to the user that their CSV is ready
    '''

    subject = f'{settings.SITE_NAME} CSV download'
    from_email = settings.DEFAULT_FROM_EMAIL
    download = Download.objects.get(id=download_id)
    filename = download.descriptive_filename()

    context = {
        'email_title': 'Download CSV',
        'username': username,
        'link_url': download_url(download_id),
        'message': f"Your file '{filename}' is ready for download.",
        'prompt': 'Click on the link below.',
        'link_text': 'Download .csv file',
        'logo_link': settings.LOGO_LINK,
        'url_i_analyzer': settings.BASE_URL,
        'site_name': settings.SITE_NAME,
        'organization': 'the Research Software Lab at the Centre for Digital Humanities (Utrecht University)'
    }

    html_message = render_to_string('download_mail.html', context)

    plain_message = strip_tags(html_message)

    result = mail.send_mail(
        subject,
        plain_message,
        from_email,
        [user_email],
        html_message=html_message
    )

    if not result:
        logger.error(
            f'Failed to send email to {user_email} about download #{download_id}'
        )
