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
    corpus = import_corpus_class(corpus_name)
    return dirname(getabsfile(corpus))


def import_corpus_class(corpus_name: str) -> Type[CorpusDefinition]:
    '''Imports a corpus definition class'''
    import_path = settings.CORPORA.get(corpus_name)
    return import_string(import_path)


def corpus_settings(corpus_name: str) -> Dict:
    '''Attribute overrides for a corpus as configured in settings'''
    corpora_settings = getattr(settings, 'CORPUS_SETTINGS', {})
    return corpora_settings.get(corpus_name, dict())


def apply_corpus_settings(corpus_class: Type[CorpusDefinition], settings: Dict):
    '''
    Creates a subclass of a corpus that overrides parent attributes according to settings.

    Overrides are applied on a class instead of an instance, as this allows you to
    override `@property` attributes with static values.
    '''
    class ConfiguredCorpus(corpus_class):
        pass

    for attr, value in settings.items():
        setattr(ConfiguredCorpus, attr, value)
    return ConfiguredCorpus


def load_corpus_definition(corpus_name: str) -> CorpusDefinition:
    '''Imports, configures and instantiates a corpus definition'''
    corpus_class = import_corpus_class(corpus_name)
    configured_class = apply_corpus_settings(corpus_class, corpus_settings(corpus_name))
    return configured_class()


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
