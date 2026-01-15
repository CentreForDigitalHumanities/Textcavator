from datetime import datetime
import os

from django.conf import settings
from corpora.gale.gale import GaleCorpus
from api.utils import find_media_file


class IllustratedLondonNews(GaleCorpus):
    title = "Illustrated London News"
    description = "Archive of Illustrated London News, a British weekly news magazine."
    min_date = datetime(1842, 5, 14)
    max_date = datetime(2003, 7, 7)
    data_directory = settings.ILLUSTRATED_LONDON_NEWS_DATA
    es_index = getattr(settings, 'ILLUSTRATED_LONDON_NEWS_ES_INDEX', 'illustrated_london_news')
    image = 'the_happy_land.png'
    description_page = 'IllustratedLondonNews.md'
    languages = ['en']
    category = 'periodical'

    scan_image_type = 'image/jpeg'

    @property
    def metafile(self):
        return os.path.join(self.data_directory, "IllustratedLondonNews.xlsx"), "IllustratedLondonNews"

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
            image_name = '{}-{}.JPG'.format(prefix, page_no)
            image_path = os.path.join(image_directory, image_name)

            full_path = find_media_file(self.data_directory, image_path, self.scan_image_type)
            if full_path is not None:
                image_list.append(full_path)
            else:
                continue
        return image_list
