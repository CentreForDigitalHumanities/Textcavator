from django.http import HttpResponse
from django.contrib.staticfiles import finders
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def index(*args, **kwargs):
    """ Thin wrapper for the static index.html that adds the CSRF cookie."""
    return HttpResponse(content=open(finders.find('index.html')))
