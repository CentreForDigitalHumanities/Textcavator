from datetime import datetime
from itertools import chain

from django.conf import settings

from corpora.gallica.gallica import Gallica


class JournauxResistance(Gallica):
    title = "Journaux clandestins de la Résistance"
    description = "Collection of French underground journals during and after German occupation, 1940-1954"
    min_date = datetime(year=1940, month=1, day=1)
    max_date = datetime(year=1954, month=12, day=31)
    publication_ids = [
        # Bulletins
        "cb32738662m",
        "cb327386649",
        "cb32738660x",
        "cb423331497",
        "cb32725373h",
        "cb32738665n",
        "cb32738663z",
        "cb327386618",
        "cb327386660",
        # Combat
        "cb34501455d",
        "cb32744514q",
        "cb32744538q",
        "cb32744563x",
        "cb32744513c",
        "cb328335253",
        # Courrier français
        "cb343853751",
        # Défense de la France
        "cb34419180r",
        # Front national
        "cb32778948q",
        # Pensée libre
        "cb32778948q",
        # Vie ouvière
        "cb32889252n",
        # Franc-tireur
        "cb327771964",
        "cb32777201w",
        # Populaire nord
        "cb328688770",
        "cb32841212n",
        "cb424376728",
        # Populaire sud
        "cb34393339w",
        # Étoiles
        "cb327704441",
        # Lettres françaises
        "cb34348821c",
        # Petites ailes
        "cb32838493h",
        "cb328878655",
        "cb327180407",
        "cb328384925",
        "cb32853250w",
        # L'Humanité
        "cb42396565j",
        "cb42456522m",
        # Liberation sud
        "cb32806584q",
        # Liberation nord
        "cb43776323g",
        "cb361401176",
        # Libérer et fédérer
        "cb328066364",
        # Liberté (Charente)
        "cb36140473",
        # Université libre
        "cb32885814s",
        # Pantagruel
        "cb328317929",
        # Valmy
        "cb32886801p",
        # Résistance
        "cb328532459",
        "cb32853253x",
    ]
    category = "periodical"
    es_index = 'resistance'
    image = "resistance.png"
    description_page = "resistance.md"

    def sources(self, start, end):
        for pub_id in self.publication_ids:
            self.corpus_id = pub_id
            docs = super().sources(start, end)
            if not docs:
                continue
            for doc in docs:
                yield doc

    def __init__(self):
        self.fields = [
            self.content(),
            self.contributor(),
            self.date(self.min_date, self.max_date),
            self.identifier(),
            self.issue(),
            self.periodical_title(),
            self.url(),
        ]
