from datetime import datetime

from django.conf import settings

from api.utils import find_media_file

from addcorpus.python_corpora.filters import MultipleChoiceFilter, RangeFilter
from addcorpus.python_corpora.corpus import CorpusDefinition, FieldDefinition
from media.image_processing import get_pdf_info, retrieve_pdf, pdf_pages, build_partial_pdf
from addcorpus.es_mappings import keyword_mapping, main_content_mapping
from addcorpus.es_settings import es_settings as make_es_settings
from media.media_url import media_url
from corpora.dutchannualreports.combined import ConcatReader
from corpora.dutchannualreports.old_data import DutchAnnualReportsOldDataReader
from corpora.dutchannualreports.new_data import NewDataReader

class DutchAnnualReports(ConcatReader, CorpusDefinition):
    title = "Dutch Annual Reports"
    description = "Annual reports of Dutch companies listed in the Amsterdam stock exchange"
    min_date = datetime(year=1957, month=1, day=1)
    max_date = datetime(year=2024, month=12, day=31)

    @property
    def data_directory(self):
        return settings.DUTCHANNUALREPORTS_DATA

    es_index = getattr(settings, 'DUTCHANNUALREPORTS_ES_INDEX', 'dutchannualreports')
    image = 'dutchannualreports.jpg'
    scan_image_type = getattr(settings, 'DUTCHANNUALREPORTS_SCAN_IMAGE_TYPE', 'application/pdf')
    description_page = 'dutchannualreports.md'
    allow_image_download = getattr(settings, 'DUTCHANNUALREPORTS_ALLOW_IMAGE_DOWNLOAD', True)
    word_model_path = getattr(settings, 'DUTCHANNUALREPORTS_WM', None)
    es_settings = make_es_settings()

    languages = ['nl', 'en']
    category = 'finance'

    mimetype = 'application/pdf'

    reader_classes = [
        DutchAnnualReportsOldDataReader,
        NewDataReader,
    ]

    fields = [
        FieldDefinition(
            name='year',
            display_name='Year',
            description='Year of the financial report.',
            results_overview=True,
            visualizations=['resultscount', 'termfrequency'],
            es_mapping={'type': 'integer'},
            search_filter=RangeFilter(
                description='Restrict the years from which search results will be returned.',
                lower=min_date.year,
                upper=max_date.year,
            ),
            visualization_sort="key",
            csv_core=True,
            sortable=True
        ),
        FieldDefinition(
            name='company',
            display_name='Company',
            description='Company to which the report belongs.',
            results_overview=True,
            visualizations=['resultscount', 'termfrequency'],
            es_mapping={'type': 'keyword'},
            search_filter=MultipleChoiceFilter(
                description='Search only within these companies.',
            ),
            csv_core=True
        ),
        FieldDefinition(
            name='company_type',
            display_name='Company Type',
            description='Financial or non-financial company?',
            es_mapping={'type': 'keyword'},
            search_filter=MultipleChoiceFilter(
                description=(
                    'Accept only financial / non-financial companies'
                ),
            ),
        ),
        FieldDefinition(
            name='page',
            display_name='Page Number',
            description='The number of the page in the scan',
            es_mapping={'type': 'integer'},
            csv_core=True,
            sortable=True
        ),
        FieldDefinition(
            name='id',
            display_name='ID',
            es_mapping=keyword_mapping(),
            description='Unique identifier of the page.',
            hidden=True,
        ),
        FieldDefinition(
            name='content',
            es_mapping=main_content_mapping(True),
            display_name='Content',
            display_type='text_content',
            visualizations=['wordcloud'],
            description='Text content of the page.',
            results_overview=True,
            search_field_core=True,
        ),
        FieldDefinition(
            name='file_path',
            es_mapping=keyword_mapping(),
            display_name='File path',
            description='Filepath of the source file containing the document,\
            relative to the corpus data directory.',
            hidden=True,
        ),
        FieldDefinition(
            name='image_path',
            mapping=keyword_mapping(),
            display_name="Image path",
            description="Path of the source image corresponding to the document,\
            relative to the corpus data directory.",
            hidden=True,
        )
    ]

    document_context = {
        'context_fields': ['company', 'year'],
        'sort_field': 'page',
        'sort_direction': 'asc',
        'context_display_name': 'report'
    }

    def request_media(self, document, corpus_name):
        image_path = document['fieldValues']['image_path']
        absolute_path = find_media_file(self.data_directory, image_path, self.mimetype)
        pdf_info = get_pdf_info(absolute_path)
         #the page corresponding to the document
        home_page = int(document['fieldValues']['page']) - 1 # values are 1-indexed in doc
        pages = pdf_pages(home_page, pdf_info['num_pages'])
        pdf_info = {
            "pageNumbers": [p for p in pages], #change from 0-indexed to real page
            "homePageIndex": home_page + 1, #change from 0-indexed to real page
            "fileName": pdf_info['filename'],
            "fileSize": pdf_info['filesize']
        }
        image_url = media_url(
            corpus_name,
            image_path,
            start_page=pages[0]-1,
            end_page=pages[-1]
        )
        return {'media': [image_url], 'info': pdf_info}


    def get_media(self, request_args):
        '''
        Given the image path and page number of the search result,
        construct a new pdf which contains 2 pages before and after.
        '''
        image_path = request_args['image_path']
        start_page = int(request_args['start_page'])
        end_page = int(request_args['end_page'])
        absolute_path = find_media_file(self.data_directory, image_path, self.mimetype)
        input_pdf = retrieve_pdf(absolute_path)
        pages = range(start_page, end_page)
        out = build_partial_pdf(pages, input_pdf)
        return out
