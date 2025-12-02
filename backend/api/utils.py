import mimetypes
import os
from rest_framework.exceptions import ParseError
from django.conf import settings

from addcorpus.models import Corpus

def check_json_keys(request, keys):
    '''
    Check that each key in keys is present in request.data
    '''

    for key in keys:
        if key not in request.data:
            raise ParseError(detail=f'Key "{key}" not specified')


def safe_path_join(base_path, suffix):
    """A safer alternative to os.path.join() that makes sure the resulting path is
    placed under base_path in the filesystem"""
    path = os.path.abspath(os.path.join(base_path, suffix))
    if os.path.commonprefix([path, base_path]) != base_path:
        raise FileNotFoundError()

    return path


def find_media_file(base_path, file_path, mime_type=None):
    path = safe_path_join(base_path, file_path)
    if not os.path.isfile(path):
        return None

    if mime_type is not None and mimetypes.guess_type(path)[0] != mime_type:
        raise ValueError(f'Unexpected MIME type when reading {file_path}')

    return path

def document_link(corpus_name: str, document_id: str) -> str:
    return f'{settings.BASE_URL}/document/{corpus_name}/{document_id}'
