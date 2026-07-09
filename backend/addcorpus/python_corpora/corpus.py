'''
Module contains the base classes from which corpora can derive;
'''

from typing import Optional, List, Dict, Union
from ianalyzer_readers import extract
from datetime import datetime, date
from os.path import isdir
import os

from django.conf import settings

from ianalyzer_readers.readers.core import Reader, Field
from ianalyzer_readers.readers.xml import XMLReader
from ianalyzer_readers.readers.csv import CSVReader
from ianalyzer_readers.readers.html import HTMLReader
from ianalyzer_readers.readers.json import JSONReader
from ianalyzer_readers.readers.rdf import RDFReader
from ianalyzer_readers.readers.xlsx import XLSXReader

from addcorpus.python_corpora.filters import Filter

import logging

logger = logging.getLogger('indexing')


class CorpusDefinition(Reader):
    '''
    Subclasses of this class define corpora and their documents by specifying:

    - How to obtain its source files.
    - What attributes its documents have.
    - How to extract said attributes from the source files.
    - What each attribute looks like in terms of the search form.
    '''

    @property
    def title(self):
        '''
        Title of the corpus
        '''
        raise NotImplementedError('CorpusDefinition missing title')

    @property
    def description(self):
        '''
        Short description of the corpus
        '''
        raise NotImplementedError('CorpusDefinition missing description')

    @property
    def min_date(self) -> Union[datetime, date, int]:
        '''
        Minimum timestamp for data files.

        Can be a datetime, date, or integer (representing the year).
        '''
        raise NotImplementedError('CorpusDefinition missing min_date')

    @property
    def max_date(self) -> Union[datetime, date, int]:
        '''
        Maximum timestamp for data files.

        Can be a datetime, date, or integer (representing the year).
        '''
        raise NotImplementedError('CorpusDefinition missing max_date')

    '''
    Language(s) used in the corpus

    Should be a list of strings. Each language should
    correspond to an ISO-639 code.
    '''
    languages = ['']

    @property
    def category(self):
        '''
        Type of documents in the corpus

        See addcorpus.constants.CATEGORIES for options
        '''
        raise NotImplementedError('CorpusDefinition missing category')

    '''
    Directory where source data is located
    If neither `data_directory` nor `data_url` is set to valid paths, this corpus cannot be indexed
    '''
    data_directory = None

    '''
    URL where source data is located
    If neither `data_directory` nor `data_url` is set to valid paths, this corpus cannot be indexed
    '''
    data_url = None

    '''
    If connecting to the data URL requires and API key, it needs to be set here
    '''
    data_api_key = None

    es_index = None
    '''
    Name of the Elasticsearch index of the corpus.

    If blank, the index name will be auto-generated based on the corpus name and
    application prefix. This can be customised, e.g. to use an existing index with a
    different naming pattern.

    If set, this is the name used by search requests. It may match an index or
    an alias.
    '''

    es_alias = None
    '''
    Additional Elasticsearch alias. Defaults to None.

    Most common use case is to assign a shared alias to several corpora.
    '''

    '''
    Dictionary containing ElasticSearch settings for the corpus' index.
    Can be overridden, usually to set analysers for fields. By default contains the
    setting to ensure `number_of_replicas` is zero on index creation (this is better
    while creating an index). Should you choose to overwrite this, consider  using
    the `addcorpus.es_settings` module.
    '''
    es_settings = {'index': {'number_of_replicas': 0}}

    '''
    A dictionary that specifies how documents can be grouped into a "context". For example,
    parliamentary speeches may be grouped into debates. The dictionary has two keys:
    - `'context_fields'`: a list of the `name`s of the fields that can be used to
    group documents. The context of a document is the set of documents that match
    its value for all the listed fields.
    - `'sort_field'`: the `name` of the field by which documents can be sorted
    within their respective group. The field should be marked as `sortable`. If `None`,
    no sorting will be applied.
    - `'sort_direction'`: direction of sorting to be applied, can be `'asc'` or `'desc'`
    - `'context_display_name'`: The display name for the context used in the interface. If
    `None`, use the displayName of the first context field.
    '''
    document_context = {
        'context_fields': None,
        'sort_field': None,
        'context_display_name': None
    }

    '''
    Specifies a default configuration for sorting search results.

    The value should be a dictionary that specifies `'field'` and `'ascending'`, e.g.:

    `{'field': 'date', 'ascending': True }`

    The field must be the `name` of a sortable field in the corpus.

    This configuration is used when sorting search results when the query context is
    empty, i.e. the user has not entered query text. Results from a query are always
    sorted on relevance by default.
    '''
    default_sort = {}

    '''
    Name of the field that contains the language of documents.

    Fields with `language='dynamic'` will use the content of this field to determine the
    language of the content.
    '''
    language_field = None

    image: Optional[str] = None
    '''
    Name of the corpus image. Should be relative path from a directory 'images'
    in the same directory as the corpus definition file.
    '''

    '''
    MIME type of scanned documents (images)
    '''
    scan_image_type = None

    '''
    path where word models are stored
    '''
    word_model_path = None

    @property
    def word_models_present(self):
        '''
        if word models are present for this corpus
        '''
        return self.word_model_path is not None and isdir(self.word_model_path)

    '''
    Allow the downloading of source images
    '''
    allow_image_download = False

    description_page: Optional[str] = None
    '''
    filename of markdown document with a comprehensive description
    '''

    citation_page: Optional[str] = None
    '''
    filename of markdown document with citation guidelines
    '''

    license_page: Optional[str] = None
    '''
    filename of markdown document with licence text
    '''

    wordmodels_page: Optional[str] = None
    '''
    filename of markdown document with documentation for word models
    '''

    terms_of_service_page: Optional[str] = None
    '''
    filename of markdown document with terms of service
    '''

    def update_body(self, **kwargs):
        ''' given one document in the index, give an instruction
        of how to update the index
        (based on script or partial data)
        '''
        return None

    def update_script(self, **kwargs):
        ''' return a (generator of a) Elasticsearch
        update_by_query script
        '''
        return None

    def update_query(self, **kwargs):
        ''' given the min date and max date of the
        time period for which the update should be performed,
        return a query restricting the result set
        Default is a match_all query.
        '''
        return {
            "query": {
                "match_all": {}
            }
        }

    def request_media(self, document, corpus_name):
        '''
        Get a dictionary with
        'media': list of urls from where media associated with a document can be fetched,
        'info': information for file download

        Arguments:
        - `document`: dict representation of document. Field values are stored in `fieldValues`
        - `corpus_name`: name of the corpus in settings. Needed to create urls with the proper corpus name.
        '''
        return {'media': None, 'info': None}

    def sources(self, start=datetime.min, end=datetime.max):
        '''
        Obtain source files for the corpus, relevant to the given timespan.

        Specifically, returns an iterator of tuples that each contain a string
        filename and a dictionary of associated metadata. The latter is usually
        empty or contains only a timestamp; but any data that is to be
        extracted without reading the file itself can be specified there.
        '''
        super().sources(start=start, end=end)

    def documentation_path(self, page_type: str) -> Optional[str]:
        '''
        Returns the path to a documentation file, relative to the corpus directory.
        '''

        pages = {
            'general': ('description', 'description_page'),
            'citation': ('citation', 'citation_page'),
            'license': ('license', 'license_page'),
            'terms_of_service': ('terms_of_service', 'terms_of_service_page'),
            'wordmodels': ('wm', 'wordmodels_page'),
        }

        if page_type in pages:
            directory, attr = pages[page_type]
            filename = self.__getattribute__(attr)
            if filename:
                return os.path.join(directory, filename)

    def process_scan(self, filename):
        '''
        Run any required processing for making scan files ready for consumption by the frontend.
        (e.g. converting to a different format)
        '''
        logger.info("process_scan() called but it's the empty base implementation")
        raise NotImplementedError()


class ParentCorpusDefinition(CorpusDefinition):
    ''' A class from which other corpus definitions can inherit.
    This class is in charge of setting fields, usually without defining an extractor.
    The subclassed CorpusDefinitions will set extractors on the fields -
    this way, CorpusDefinitions can share the same mappings and filters,
    while the logic to collect sources and populate the fields can be different.
    The ParentCorpusDefinition can also be used to allow cross-corpus search and filtering.
    '''
    # define fields property so it can be set in __init__
    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        self._fields = value

    def __init__(self):
        ''' Specify a list of fields which all subclasses share
            A subclass of ParentCorpusDefinition will provide extractors for the fields,
            and potentially prune down the list of fields to those which have an extractor
        '''
        self.fields = []


class XMLCorpusDefinition(CorpusDefinition, XMLReader):
    '''
    An XMLCorpus is any corpus that extracts its data from XML sources.
    '''


class HTMLCorpusDefinition(CorpusDefinition, HTMLReader):
    '''
    An HTMLCorpus is any corpus that extracts its data from HTML sources.
    '''


class CSVCorpusDefinition(CorpusDefinition, CSVReader):
    '''
    An CSVCorpus is any corpus that extracts its data from CSV sources.
    '''


class XLSXCorpusDefinition(CorpusDefinition, XLSXReader):
    '''
    An CSVCorpus is any corpus that extracts its data from an XLSX spreadsheet.
    '''


class JSONCorpusDefinition(CorpusDefinition, JSONReader):
    '''
    Corpus definition for json encoded data.
    '''


class RDFCorpusDefinition(CorpusDefinition, RDFReader):
    '''
    A RDFCorpus is any corpus that extracts its data from Linked Data files.
    '''

# Fields ######################################################################


class FieldDefinition(Field):
    '''
    Definition for a single field in a corpus.

    Parameters:
        name: A shorthand name. Must be a slug.
        display_name: The name that should be shown to the user. If you leave this out,
            the `name` will be used.
        display_type:  Determines how the field should be rendered. This can be any
            supported elasticsearch mapping type, `'url'`, or `'text_content'`. If you
            leave this blank, the mapping type of `es_mapping` will be used, so this
            only needs to be specified for URL and text content fields.
        description: An explanation of the field for users.
        indexed: Whether the field is skipped during source extraction and indexing.
        hidden: Whether the field is hidden in the frontend.
        results_overview: Whether the field appears in the preview of a document.
        csv_core: Whether the field is pre-selected for CSV downloads of search results.
        search_field_core: Whether the field is immediately shown in field selection for
            the search query. If `False`, the field is only shown when the user selects
            "show all fields".
        visualizations: Visualisations that are enabled for this field. Options:
            resultscount, termfrequency, wordcloud, ngram. For date fields and
            categorical/ordinal fields (usually keyword type), you can use
            `['resultscount', 'termfrequency']`. For text fields, you can use
            `['wordcloud', 'ngram']`. However, the ngram visualisation also requires that
            the corpus has a date field.
        visualization_sort: If the visualisations include resultscount or termfrequency
            and the field is not a date field, this determines how the histogram is
            sorted. Options are `'value'` (sort from most to least frequent) or `'key'`
            (sort alphabetically).
        es_mapping: The mapping of the field in Elasticsearch. It's recommended to use one
            of the functions in `addcorpus.es_mappings` to construct this.
        language: The language of the field's content. Can be `None`, an IETF tag, or
            `"dynamic"`. None means the language is unknown or NA. Dynamic means the
            `language_field` of the corpus specifies the IETF tag for this field's
            language per document.
        search_filter: Configuration of the search filter used for the field (if any).
            Should be `Filter` instance.
        extractor: Configuration to extract the field's data from source documents. Should
            be an `Extractor` instance.
        sortable: Whether this field is shown as an option to sort search results. If
            `None`, the value is inferred from the mapping type.
        searchable: Whether this field is shown in the selection for search fields. If
            `None`, the vlaue is inferred from the mapping type.
        downloadable: Whether this field may be included when downloading results.
        required: Whether this field is required during source extraction. Note that not
            all Reader subclasses currently support this.
    '''

    def __init__(self,
                 name: str,
                 display_name: Optional[str] = None,
                 display_type: Optional[str] = None,
                 description: str = '',
                 indexed: bool = True,
                 hidden: bool = False,
                 results_overview: bool = False,
                 csv_core: bool = False,
                 search_field_core: bool = False,
                 visualizations: List[str] = [],
                 visualization_sort: Optional[str] = None,
                 es_mapping: Dict = {'type': 'text'},
                 language: Optional[str] = None,
                 search_filter: Optional[Filter] = None,
                 extractor: extract.Extractor = extract.Constant(None),
                 sortable: Optional[bool] = None,
                 searchable: Optional[bool] = None,
                 downloadable: bool = True,
                 required: bool = False,
                 **kwargs
                 ):

        super().__init__(
            name=name,
            extractor=extractor,
            required=required,
            skip=not indexed,
        )

        mapping_type = es_mapping['type']

        self.display_name = display_name or name
        self.display_type = display_type or mapping_type
        self.description = description
        self.search_filter = search_filter
        self.results_overview = results_overview
        self.csv_core = csv_core
        self.search_field_core = search_field_core
        self.visualizations = visualizations
        self.visualization_sort = visualization_sort
        self.es_mapping = es_mapping
        self.language = language
        self.hidden = not indexed or hidden

        self.sortable = sortable if sortable is not None else \
            not hidden and indexed and \
            mapping_type in ['integer', 'float', 'date']

        # Fields are searchable if they are not hidden and if they are mapped as 'text'.
        # Keyword fields without a filter are also searchable.
        self.searchable = searchable if searchable is not None else \
            not hidden and indexed and \
            ((mapping_type == 'text') or
             (mapping_type == 'keyword' and self.search_filter is None))
        # Add back reference to field in filter
        self.downloadable = downloadable

        if self.search_filter:
            self.search_filter.field = self


# Helper functions ############################################################


def string_contains(target):
    '''
    Return a predicate that performs a case-insensitive search for the target
    string and returns whether it was found.
    '''
    def f(string):
        return bool(target.lower() in string.lower() if string else False)
    return f


def until(year):
    '''
    Returns a predicate to determine from metadata whether its 'date' field
    represents a date before or on the given year.
    '''
    def f(metadata):
        date = metadata.get('date')
        return date and date.year <= year
    return f


def after(year):
    '''
    Returns a predicate to determine from metadata whether its 'date' field
    represents a date after the given year.
    '''
    def f(metadata):
        date = metadata.get('date')
        return date and date.year > year
    return f


def consolidate_start_end_years(
        start: Union[datetime, date, int],
        end: Union[datetime, date, int],
        min_date: datetime,
        max_date: datetime
):
    ''' given a start and end date provided by the user, make sure
    - that start is not before end
    - that start is not before min_date (corpus variable)
    - that end is not after max_date (corpus variable)
    '''
    if isinstance(start, int):
        start = datetime(year=start, month=1, day=1)
    elif isinstance(start, date):
        start = datetime(year=start.year, month=start.month, day=start.day)
    if isinstance(end, int):
        end = datetime(year=end, month=12, day=31)
    elif isinstance(end, date):
        end = datetime(year=end.year, month=end.month, day=end.day)

    if start > end:
        tmp = start
        start = end
        end = tmp
    if start < min_date:
        start = min_date
    if end > max_date:
        end = max_date


def transform_to_date_range(earliest, latest):
    if not earliest:
        earliest = '0001-01-01'
    if not latest:
        latest = datetime.today().isoformat()[:10]
    return {
        'gte': earliest,
        'lte': latest
    }
