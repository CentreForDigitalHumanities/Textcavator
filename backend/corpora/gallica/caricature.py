from datetime import datetime

from django.conf import settings

from corpora.gallica.gallica import Gallica


class Caricature(Gallica):
    title = "La Caricature morale, politique et littéraire"
    description = "Satirical periodical, 1830-1843"
    min_date = datetime(year=1830, month=1, day=1)
    max_date = datetime(year=1843, month=12, day=31)
    corpus_id = "cb344523348"
    category = "periodical"
    es_index = 'caricature'
    description_page = 'caricature.md'
    image = "caricature.jpg"

    def __init__(self):
        self.fields = [
            self.content(),
            self.contributor(),
            self.date(self.min_date, self.max_date),
            self.identifier(),
            self.issue(),
            self.publisher(),
            self.url(),
        ]
