from datetime import datetime

from django.conf import settings

from corpora.gallica.gallica import Gallica


class Figaro(Gallica):
    title = "Le Figaro"
    description = "Archive of Le Figaro, a French daily newspaper."
    min_date = datetime(year=1854, month=1, day=1)
    max_date = datetime(year=1954, month=12, day=31)
    corpus_id = "cb34355551z"
    category = "periodical"
    es_index = 'figaro'
    image = "figaro.jpg"
    description_page = 'figaro.md'

    def __init__(self):
        self.fields = [
            self.content(),
            self.contributor(),
            self.date(self.min_date, self.max_date),
            self.identifier(),
            self.issue(),
            self.url(),
        ]
