'''
This module defines functions to check if a corpus is ready for indexing.
'''

import warnings
import os

from addcorpus.validation.creation import primary_mapping_type


class CorpusNotIndexableError(Exception):
    '''
    The Corpus is not meeting the requirements for indexing.
    '''

    pass

def validate_has_configuration(corpus):
    if not corpus.configuration_obj:
        raise CorpusNotIndexableError('Corpus has no attached configuration')

def validate_essential_fields(fields):
    '''
    Validates that the corpus is not missing essential fields.

    Raises CorpusNotIndexableError if:

    - the corpus has no content field(s)
    - the corpus has no metadata field(s)

    Warns if:

    - the corpus has no ID field
    '''

    if not len(fields):
        raise CorpusNotIndexableError('Corpus has no fields')

    _raise_if_no_content_field(fields)
    _raise_if_no_metadata_field(fields)
    _warn_if_no_id_field(fields)

def _raise_if_no_content_field(fields):
    if not any(field.is_main_content for field in fields):
        raise CorpusNotIndexableError('Corpus has no main content field')

def _raise_if_no_metadata_field(fields):
    if all(field.is_main_content for field in fields):
        raise CorpusNotIndexableError('Corpus has no metadata fields')

def _warn_if_no_id_field(fields):
    if not any(field.name == 'id' for field in fields):
        warnings.warn(
            "Corpus has no 'id' field. Document IDs will be unstable between index "
            "versions."
        )

def validate_language_field(corpus):
    config = corpus.configuration
    field_name = config.language_field
    if field_name:
        try:
            field = config.fields.get(name=field_name)
        except:
            raise CorpusNotIndexableError(
                f'Invalid language field: no field named "{field_name}"'
            )
        mapping_type = primary_mapping_type(field.es_mapping)
        if mapping_type != 'keyword':
            raise CorpusNotIndexableError(
                f'Invalid language field: "{field_name}" has {mapping_type} mapping '
                '(should be keyword)'
            )
    elif config.fields.filter(language='dynamic').exists():
        raise CorpusNotIndexableError(
            'Cannot use "dynamic" language for fields without configuring a '
            'field_language for the corpus'
        )

def validate_has_data(corpus):
    '''
    If the corpus does not have a Python definition, validate that it has a data
    directory, or at least one confirmed data file.
    '''

    if corpus.has_python_definition:
        return

    config = corpus.configuration
    datafiles = corpus.datafiles

    if config.data_directory:
        if not os.path.isdir(config.data_directory):
            raise CorpusNotIndexableError(
                'Configured data directory does not exist.'
            )
    elif not datafiles.filter(confirmed=True).exists():
        raise CorpusNotIndexableError(
            'Missing data files or data directory'
        )
