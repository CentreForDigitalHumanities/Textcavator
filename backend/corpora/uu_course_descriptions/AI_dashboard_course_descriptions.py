from datetime import datetime
import os

from openpyxl import Workbook, load_workbook


from ianalyzer import settings
from addcorpus.python_corpora.corpus import FieldDefinition, XLSXCorpusDefinition
from addcorpus.es_mappings import text_mapping, main_content_mapping, keyword_mapping, int_mapping
from addcorpus.python_corpora.filters import MultipleChoiceFilter


from corpora.uu_course_descriptions.uu_course_descriptions import get_from_mapping_or_return, FACULTIES, EXAM_GOALS, LEVELS
from addcorpus.python_corpora.corpus import FieldDefinition
from ianalyzer_readers.extract import CSV, Combined, Pass, Constant, Metadata

def metadata_lookup(values):
    id = values[0]
    metadata_dict = values[1]
    return metadata_dict[id]

class AIDashboardCourseDescriptions(XLSXCorpusDefinition):
    title = 'AI Dashboard Course Descriptions'
    description = 'All courses taught at Utrecht University in 2020-2024'
    category = 'other'
    min_date = datetime(2024, 9, 1)
    max_date = datetime(2025, 8, 31)
    image = 'Academiegebouw_Utrecht_University.JPG'
    description_page = 'description.md'
    languages = ['nl', 'en', 'de', 'fr', 'es', 'it']
    es_index =  getattr(settings, 'AI_DASHBOARD_ES_INDEX', 'AI_dashboard')

    data_directory = settings.AI_DASHBOARD_DATA

    def sources(self, *args, **kwargs):
        for year in ['2020']: #, '2021', '2022', '2023', '2024']:
            path = os.path.join(self.data_directory, "{} overzicht met blok.xlsx".format(year))

            # NB: the file structure is two xlsx files, both containing half of the relevant data
            # the file with the main content is read as the 'main file', the other is the
            # 'metadata file'
            # with two separate files that both contain half of the metadata, reading the
            # metadata will take a while.
            meta_path = os.path.join(self.data_directory, "{} overzicht zonder blok.xlsx".format(year))
            metadict = {}
            wb = load_workbook(meta_path)
            ws = wb.active
            header_values = next(ws.values)
            for header in header_values:
                metadict[header] = {}
            for row in ws.values:
                id = row[0]
                for index, value in enumerate(row):
                    metadict[header_values[index]][id] = value

            yield path, metadict

    fields = [
        FieldDefinition(
            name='id',
            display_name='Course ID',
            extractor=CSV('Cursus'),
            es_mapping=keyword_mapping(),
            csv_core=True,
            results_overview=True,
        ),
        FieldDefinition(
            name='academic_year',
            display_name='Academic year',
            extractor=CSV('Collegejaar'),
            es_mapping=int_mapping(),
        ),
        FieldDefinition(
            name='name',
            display_name='Name',
            extractor=CSV('Korte naam'),
            es_mapping=text_mapping(),
            results_overview=True,
            search_field_core=True,
            csv_core=True,
        ),
        FieldDefinition(
            name='full_name',
            display_name='Full name',
            extractor=CSV('Lange naam'),
            es_mapping=text_mapping(),
            search_field_core=True,
            csv_core=True,
        ),
        FieldDefinition(
            name='faculty',
            display_name='Faculty',
            extractor=Combined(
                CSV('Cursus'),
                Metadata('Faculteit'),
                transform=metadata_lookup),
            es_mapping=keyword_mapping(),
            search_filter=MultipleChoiceFilter(),
            visualizations=['resultscount', 'termfrequency'],
        ),
        FieldDefinition(
            name='exam_goal',
            display_name='Exam goal',
            description='',
            extractor=CSV('Examendoel', transform=get_from_mapping_or_return(EXAM_GOALS)),
            es_mapping=keyword_mapping(),
            search_filter=MultipleChoiceFilter(),
            visualizations=['resultscount', 'termfrequency'],
        ),
        FieldDefinition(
            name='level',
            display_name='Level',
            extractor=CSV('Categorie', transform=get_from_mapping_or_return(LEVELS)),
            es_mapping=keyword_mapping(),
            search_filter=MultipleChoiceFilter(),
            visualizations=['resultscount', 'termfrequency'],
        ),
        FieldDefinition(
            name='type',
            display_name='Course type',
            extractor=Combined(
                CSV('Cursus'),
                Metadata('Cursustype'),
                transform=metadata_lookup),
            es_mapping=keyword_mapping(),
            search_filter=MultipleChoiceFilter(option_count=100),
            visualizations=['resultscount', 'termfrequency'],
        ),
        FieldDefinition(
            name='department_description',
            display_name='Department',
            description='Coordinating department for the course',
            extractor=Combined(
                CSV('Cursus'),
                Metadata('Omschrijving coördinerend onderdeel'),
                transform=metadata_lookup),
            es_mapping=keyword_mapping(enable_full_text_search=True),
            results_overview=True,
            search_filter=MultipleChoiceFilter(option_count=100),
            visualizations=['resultscount', 'termfrequency'],
        ),
        FieldDefinition(
            name='department',
            display_name='Department (abbreviation)',
            description='Abbreviated name of the coordinating department',
            extractor=Combined(
                CSV('Cursus'),
                Metadata('Omschrijving coördinerend onderdeel'),
                transform=metadata_lookup),
            es_mapping=keyword_mapping(),
        ),
        FieldDefinition(
            name='term',
            display_name='Term',
            description='Term in which the course is taught',
            extractor=CSV('Aanvangsblok'),
            es_mapping=keyword_mapping(),
            search_filter=MultipleChoiceFilter(),
            visualizations=['resultscount', 'termfrequency'],
            visualization_sort='key',
        ),
        FieldDefinition(
            name='contact',
            display_name='Contact',
            description='Name of the contact person for the course',
            extractor=Combined(
                CSV('Cursus'),
                Metadata('Contactpersoon'),
                transform=metadata_lookup),
            es_mapping=keyword_mapping(enable_full_text_search=True),
            downloadable=False,
        ),
        FieldDefinition(
            name='content',
            display_name='Course content',
            description='Description of the contents of the course',
            extractor=CSV('Inhoud'),
            es_mapping=main_content_mapping(token_counts=True),
            display_type='text_content',
            results_overview=True,
            visualizations=['wordcloud'],
            search_field_core=True,
            csv_core=True,
        )
    ]

