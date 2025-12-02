from django.template import Template, Context
from datetime import date

from django.conf import settings

def render_documentation_context(raw_template):
    template = Template(raw_template)
    today = date.today()
    context = Context({
        'frontend_url': settings.BASE_URL,
        'site_name': settings.SITE_NAME,
        'date': {
            'year': today.year,
            'month': today.strftime('%B'),
            'day': today.day
        }
    })
    return template.render(context)
