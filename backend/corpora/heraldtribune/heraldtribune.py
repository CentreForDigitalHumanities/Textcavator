from datetime import datetime
import os

from ianalyzer_readers import extract
from django.conf import settings
from corpora.gale.gale import GaleCorpus, GaleMetadata, when_not_empty, fix_path_sep
from addcorpus.python_corpora.corpus import FieldDefinition
from api.utils import find_media_file


def clean_date(issue_date):
    return datetime.strptime(str(issue_date), '%Y%m%d').strftime('%Y-%m-%d')


class HeraldTribuneMetadata(GaleMetadata):
    required_field = 'StartDate'
    fields = [
        FieldDefinition(
            name='title',
            extractor=extract.CSV('Publication Title')
        ),
        FieldDefinition(
            name='date',
            extractor=extract.CSV(
                'StartDate',
                transform=clean_date
            )
        ),
        FieldDefinition(
            name='image_path',
            extractor=extract.CSV(
                'ImageLocation',
                transform=when_not_empty(fix_path_sep),
            )
        ),
        FieldDefinition(
            name='data_location',
            extractor=extract.CSV(
                'XMLLocation',
                transform=when_not_empty(fix_path_sep),
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
                transform=lambda filename: filename.split("_")[0]
            )
        ),
    ]


class HeraldTribune(GaleCorpus):
    title = "International Herald Tribune Historical Archive"
    description = "International Herald Tribune Historical Archive"
    min_date = datetime(1887, 11, 11)
    max_date = datetime(2013, 10, 14)
    data_directory = settings.HERALD_TRIBUNE_DATA
    es_index = getattr(settings, 'HERALD_TRIBUNE_ES_INDEX', 'heraldtribune')
    image = 'Neuilly-sur-Seine_International_Herald_Tribune.jpg'
    description_page = 'HeraldTribune.md'
    languages = ['en']
    category = 'periodical'

    scan_image_type = 'image/jpeg'

    metadata_corpus = HeraldTribuneMetadata

    @property
    def metafile(self):
        return os.path.join(self.data_directory, "InternationalHeraldTribune.xlsx"), "Newspapers"

    def process_scan(self, src):
        return src

    def resolve_media_path(self, field_vals, corpus_name):
        image_directory = field_vals['image_path']
        starting_page = field_vals['id'][:-4]
        start_index = int(starting_page.split("-")[-1])
        page_count = int(field_vals['page_count'])

        image_list = []
        zfill = 5
        step = 10
        ext = 'jpg'

        for page in range(page_count):
            page_no = str(start_index + page * step).zfill(zfill)
            prefix = starting_page.rsplit('-', 1)[0]
            image_name = '{}-{}.{}'.format(prefix, page_no, ext)
            image_path = os.path.join(image_directory, image_name)
            full_path = find_media_file(self.data_directory, image_path, self.scan_image_type)
            if full_path is not None:
                image_list.append(full_path)
        return image_list
