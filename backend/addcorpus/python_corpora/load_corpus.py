import logging
import re
import sys
from importlib import util
from os.path import abspath, dirname

from addcorpus.python_corpora.corpus import CorpusDefinition
from django.conf import settings

logger = logging.getLogger(__name__)
from addcorpus.python_corpora.corpus import CorpusDefinition


def corpus_path(corpus_name):
    return abspath(settings.CORPORA.get(corpus_name))

def corpus_dir(corpus_name):
    """Gets the absolute path to the corpus definition directory

    Arguments:
        corpus_name {str} -- Key of the corpus in CORPORA object in settings
    """
    return dirname(corpus_path(corpus_name))

def load_corpus_definition(corpus_name) -> CorpusDefinition:
    filepath = corpus_path(corpus_name)
    try:
        corpus_spec = util.spec_from_file_location(
            corpus_name,
            filepath)

        corpus_mod = util.module_from_spec(corpus_spec)
    except FileNotFoundError:
        logger.critical(
            'No module describing the corpus "{0}" found in the specified file path:\
            {1}'.format(corpus_name, filepath)
        )
        raise

    corpus_spec.loader.exec_module(corpus_mod)
    # assume the class name is the same as the corpus name,
    # allowing for differences in camel case vs. lower case
    regex = re.compile('[^a-zA-Z]')
    corpus_name = regex.sub('', corpus_name).lower()
    endpoint = next((attr for attr in dir(corpus_mod)
                     if attr.lower() == corpus_name), None)
    corpus_class = getattr(corpus_mod, endpoint)
    return corpus_class()

def _try_loading_corpus_definition(corpus_name, stderr=sys.stderr):
    try:
        return load_corpus_definition(corpus_name)
    except Exception as e:
        logger.exception('Could not load corpus %s: %s', corpus_name, e)

def load_all_corpus_definitions(stderr=sys.stderr):
    '''
    Return a dict with corpus names and corpus definition objects.
    '''
    corpus_definitions_unfiltered = {
        corpus_name: _try_loading_corpus_definition(corpus_name, stderr)
        for corpus_name in settings.CORPORA.keys()
    }

    # filter any corpora without a valid definition
    corpus_definitions = {
        name: definition
        for name, definition in corpus_definitions_unfiltered.items()
        if definition
    }

    return corpus_definitions
