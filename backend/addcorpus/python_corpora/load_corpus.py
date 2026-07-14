import logging
import sys
from os.path import dirname
from django.utils.module_loading import import_string
from typing import Type, Optional, Dict
from inspect import getabsfile

from addcorpus.python_corpora.corpus import CorpusDefinition
from django.conf import settings

logger = logging.getLogger(__name__)


def corpus_dir(corpus_name: str) -> str:
    """Gets the absolute path to the corpus definition directory

    Arguments:
        corpus_name {str} -- Key of the corpus in CORPORA object in settings
    """
    corpus = load_corpus_definition(corpus_name)
    return dirname(getabsfile(corpus.__class__))


def load_corpus_definition(corpus_name) -> Type[CorpusDefinition]:
    import_path = settings.CORPORA.get(corpus_name)
    return import_string(import_path)()


def _try_loading_corpus_definition(corpus_name, stderr=sys.stderr) -> Optional[CorpusDefinition]:
    try:
        return load_corpus_definition(corpus_name)
    except Exception as e:
        logger.exception('Could not load corpus %s: %s', corpus_name, e)


def load_all_corpus_definitions(stderr=sys.stderr) -> Dict[str, CorpusDefinition]:
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
