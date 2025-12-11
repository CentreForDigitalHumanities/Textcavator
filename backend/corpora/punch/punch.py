from datetime import datetime
import os

from ianalyzer_readers import extract
from django.conf import settings
from corpora.gale.gale import GaleCorpus, GaleMetadata, fix_path_sep
from addcorpus.python_corpora.corpus import FieldDefinition
from api.utils import find_media_file


class Punch(GaleCorpus):
    title = "Punch Historical Archive"
    description = "Archive of Punch, a British satirical magazine."
    min_date = datetime(1841, 7, 1)
    max_date = datetime(1992, 4, 8)
    data_directory = settings.PUNCH_DATA
    es_index = getattr(settings, 'PUNCH_ES_INDEX', 'punch')
    image = 'Collected_volumes_of_Punch.jpg'
    description_page = 'Punch.md'
    languages = ['en']
    category = 'periodical'

    scan_image_type = 'image/jpeg'

    metadata_corpus = GaleMetadata

    @property
    def metafile(self):
        return os.path.join(self.data_directory, "PunchHistoricalArchive.xlsx"), "Newspapers"

    def process_scan(self, src):
        return src

    def resolve_media_path(self, field_vals, corpus_name):
        image_directory = field_vals['image_path']
        starting_page = field_vals['id'][:-4]
        start_index = int(starting_page.split("-")[-1])
        page_count = int(field_vals['page_count'])

        image_list = []
        for page in range(page_count):
            page_no = str(start_index + page).zfill(4)
            prefix = starting_page.rsplit('-', 1)[0]
            image_name = '{}-{}.jpg'.format(prefix, page_no)
            image_path = os.path.join(image_directory, image_name)

            print(image_path)
            full_path = find_media_file(self.data_directory, image_path, self.scan_image_type)
            if full_path is not None:
                image_list.append(full_path)
            else:
                continue
        return image_list
