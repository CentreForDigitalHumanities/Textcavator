from datetime import datetime
import os

from ianalyzer_readers import extract
from django.conf import settings
from corpora.gale.gale import GaleCorpus, GaleMetadata, when_not_empty, clean_date, fix_path_sep
from addcorpus.python_corpora.corpus import FieldDefinition
from api.utils import find_media_file


class EconomistMetadata(GaleMetadata):
    fields = [
        FieldDefinition(
            name='title',
            extractor=extract.CSV('PublicationTitle')
        ),
        FieldDefinition(
            name='date',
            extractor=extract.CSV(
                'IssueDate',
                transform=when_not_empty(clean_date)
            )
        ),
        FieldDefinition(
            name='image_path',
            extractor=extract.CSV(
                'Product Data (XML, JPGs or TIFs)',
                transform=when_not_empty(fix_path_sep)
            )
        ),
        FieldDefinition(
            name='data_location',
            extractor=extract.CSV(
                'TDM XML Location',
                transform=when_not_empty(fix_path_sep)
            )
        ),
        FieldDefinition(
            name='filename',
            extractor=extract.CSV('Filename')
        ),
        FieldDefinition(
            name='issue_id',
            extractor=extract.CSV(
                'Filename',
                transform=when_not_empty(lambda filename: filename.split("_")[0])
            )
        ),
    ]


class Economist(GaleCorpus):
    title = "The Economist Archive"
    description = "The Economist Archive"
    min_date = datetime(1843, 8, 1)
    max_date = datetime(2021, 1, 1)
    data_directory = settings.ECONOMIST_DATA
    es_index = getattr(settings, 'ECONOMIST_ES_INDEX', 'economist')
    image = 'A_stack_of_Economist_papers.jpg'
    description_page = 'Economist.md'
    languages = ['en']
    category = 'periodical'

    scan_image_type = 'image/jpeg'

    metadata_corpus = EconomistMetadata

    @property
    def metafile(self):
        return os.path.join(self.data_directory, "GDA_Economist_1843-2020.xlsx"), "NewspapersPeriodicals"

    def process_scan(self, src):
        return src

    def resolve_media_path(self, field_vals, corpus_name):
        image_directory = field_vals['image_path']
        starting_page = field_vals['id'][:-4]
        start_index = int(starting_page.split("-")[-1])
        page_count = int(field_vals['page_count'])

        image_list = []
        year = int(field_vals['date'].split('-')[0])
        zfill = 4 if year <= 2014 else 5
        step = 1 if year <= 2014 else 10
        ext = 'JPG' if year <= 2014 else 'jpg'

        for page in range(page_count):
            page_no = str(start_index + page * step).zfill(zfill)
            prefix = starting_page.rsplit('-', 1)[0]
            image_name = '{}-{}.{}'.format(prefix, page_no, ext)
            image_path = os.path.join(image_directory, image_name)
            full_path = find_media_file(self.data_directory, image_path, self.scan_image_type)
            if full_path is not None:
                image_list.append(full_path)
        return image_list
