import os
from django.db import transaction
from django.core.files.images import ImageFile
import warnings
import sys
from elastic_transport import ConnectionError

from es.client import elasticsearch
from es.search import total_hits
from addcorpus.python_corpora.corpus import CorpusDefinition, FieldDefinition
from addcorpus.models import Corpus, CorpusConfiguration, Field, CorpusDocumentationPage
from addcorpus.python_corpora.load_corpus import (
    load_all_corpus_definitions, corpus_dir, load_corpus_definition
)
from addcorpus.utils import normalize_date_to_year, clear_corpus_image

def _save_corpus_configuration(corpus: Corpus, corpus_definition: CorpusDefinition):
    '''
    Save a corpus configuration in the SQL database.

    Parameters:
        corpus: a Corpus database object
        corpus_definition: a corpus object, output of `load_corpus`

    If the corpus already has a CorpusConfiguration, its contents will be overwritten
    based on the python definition. If not, a new configuration will be created.

    This function is idempotent: a given corpus definition will always create the same
    configuration, regardless of what is currently saved in the database.
    '''

    clear_corpus_image(corpus)

    # create a clean CorpusConfiguration object, but use the existing PK if possible
    pk = corpus.configuration_obj.pk if corpus.configuration_obj else None
    configuration = CorpusConfiguration(pk=pk, corpus=corpus)
    _copy_corpus_attributes(corpus_definition, configuration)
    _import_corpus_date_range(corpus_definition, configuration)
    configuration.save()
    configuration.full_clean()

    _save_corpus_fields_in_database(corpus_definition, configuration)
    _save_corpus_image(corpus_definition, configuration)
    _save_corpus_documentation(corpus_definition, configuration)
    _save_has_named_entities(configuration)

def get_defined_attributes(object, attributes):
    get = lambda attr: object.__getattribute__(attr)
    has_attribute = lambda attr: attr in dir(object) and get(attr) != None

    return {
        attr: get(attr)
        for attr in attributes
        if has_attribute(attr)
    }

def _copy_corpus_attributes(corpus_definition: CorpusDefinition, configuration: CorpusConfiguration):
    attributes_to_copy = [
        'description',
        'allow_image_download',
        'category',
        'document_context',
        'es_alias',
        'es_index',
        'languages',
        'scan_image_type',
        'title',
        'word_models_present',
        'default_sort',
        'language_field',
        'data_directory',
    ]

    try:
        defined = get_defined_attributes(corpus_definition, attributes_to_copy)
    except Exception as e:
        raise e

    for attr, value in defined.items():
        configuration.__setattr__(attr, value)

def _import_corpus_date_range(definition: CorpusDefinition, configuration: CorpusConfiguration):
    '''
    Sets the `min_year` and `max_year` attributes on a CorpusConfiguration based on
    (respectively) the `min_date` and `max_date` attributes of the CorpusDefinition.
    '''

    configuration.min_year = normalize_date_to_year(definition.min_date)
    configuration.max_year = normalize_date_to_year(definition.max_date)


def _save_corpus_fields_in_database(corpus_definition: CorpusDefinition, configuration: CorpusConfiguration):
    for index, field in enumerate(corpus_definition.fields):
        _save_field_in_database(field, configuration, position=index)

    for field in configuration.fields.exclude(name__in=corpus_definition.fieldnames):
        field.delete()

def _field_pk(name: str, configuration: CorpusConfiguration):
    try:
        return Field.objects.get(corpus_configuration=configuration, name=name).pk
    except Field.DoesNotExist:
        return None

def _save_field_in_database(field_definition: FieldDefinition, configuration: CorpusConfiguration, position: int):
    attributes_to_copy = [
        'name', 'display_name', 'display_type',
        'description', 'results_overview',
        'csv_core', 'search_field_core',
        'visualizations', 'visualization_sort',
        'es_mapping', 'indexed', 'hidden',
        'required', 'sortable',
        'searchable', 'downloadable',
        'language',
    ]

    copy_attributes = get_defined_attributes(field_definition, attributes_to_copy)

    filter_definition = field_definition.search_filter.serialize() if field_definition.search_filter else {}

    field = Field(
        pk=_field_pk(field_definition.name, configuration),
        corpus_configuration=configuration,
        search_filter=filter_definition,
        position=position,
        **copy_attributes,
    )

    field.save()
    field.full_clean()
    return field



def _save_corpus_image(corpus_definition: CorpusDefinition, configuration: CorpusConfiguration):
    corpus_name = configuration.corpus.name
    filename = corpus_definition.image
    if filename:
        path = os.path.join(corpus_dir(corpus_name), 'images', filename)
        _, ext = os.path.splitext(path)
        save_as = corpus_name + ext
        with open(path, 'rb') as f:
            configuration.image = ImageFile(f, name=save_as)
            configuration.save()

def _save_corpus_documentation(corpus_definition: CorpusDefinition, configuration: CorpusConfiguration):
    corpus_name = configuration.corpus.name

    for name, _ in CorpusDocumentationPage.PageType.choices:
        path_in_corpus_dir = corpus_definition.documentation_path(name)
        if path_in_corpus_dir:
            path = os.path.join(corpus_dir(corpus_name), path_in_corpus_dir)
            with open(path, 'r') as f:
                content = f.read()

            page, _ = CorpusDocumentationPage.objects.get_or_create(
                corpus_configuration=configuration, type=name
            )
            page.content = content
            page.save()
        else:
            pages = CorpusDocumentationPage.objects.filter(
                corpus_configuration=configuration, type=name
            )
            if pages.exists():
                pages.delete()


def _save_has_named_entities(configuration: CorpusConfiguration):
    # we check if any fields exist for filtering named entities
    if any(field.name.endswith(':ner-kw') for field in configuration.fields.all()):
        client = elasticsearch(configuration.corpus.name)
        try:
            ner_exists = client.search(
                index=configuration.es_index,
                query={"exists": {"field": "*:ner-kw"}},
                size=0
            )
            if total_hits(ner_exists):
                configuration.has_named_entities = True
                configuration.save()
        except ConnectionError:
            warnings.warn('Could not check named entities; cannot connect to Elasticsearch')
        except Exception as e:
            warnings.warn(Warning('Could not check named enities due to unexpected error:', e))


def _prepare_for_import(corpus: Corpus):
    corpus.has_python_definition = True
    corpus.active = False
    corpus.save()

def _activate_if_ready(corpus):
    '''
    Check if the corpus passes ready_to_publish() check and set active property
    accordingly.
    '''
    corpus.active = corpus.ready_to_publish()
    corpus.save()

def _clear_python_definition(corpus):
    '''
    Mark a corpus as one without a python definition and deactivate it.
    '''
    corpus.has_python_definition = False
    corpus.active = False
    corpus.save()


def _save_or_skip_corpus(corpus_name, corpus_definition, verbose=False, stdout=sys.stdout, stderr=sys.stderr):
    '''
    Try saving a corpus definition to the database.

    This will create a new CorpusConfiguration object or replace an existing one.
    Changes are rolled back on failure.
    '''

    corpus, _ = Corpus.objects.get_or_create(name=corpus_name)

    try:
        _prepare_for_import(corpus)
        with transaction.atomic():
            _save_corpus_configuration(corpus, corpus_definition)
            _activate_if_ready(corpus)
        if verbose:
            print(f'Saved corpus: {corpus_name}', file=stdout)
    except Exception as e:
        print(f'Failed saving corpus: {corpus_name}', file=stderr)
        print(f'Error: {e}', file=stderr)


def load_and_save_all_corpora(verbose=False, stdout=sys.stdout, stderr=sys.stderr):
    '''
    load all python corpus definitions and save them to the database
    '''

    corpus_definitions = load_all_corpus_definitions(stderr=stderr)

    for corpus_name, corpus_definition in corpus_definitions.items():
        _save_or_skip_corpus(corpus_name, corpus_definition, verbose=verbose, stdout=stdout, stderr=stderr)

    not_included = Corpus.objects.filter(has_python_definition=True).exclude(name__in=corpus_definitions.keys())
    for corpus in not_included:
        _clear_python_definition(corpus)


def load_and_save_single_corpus(corpus_name: str):
    '''
    Load and save a single corpus that is included in the settings.
    '''
    definition = load_corpus_definition(corpus_name)
    _save_or_skip_corpus(corpus_name, definition)
