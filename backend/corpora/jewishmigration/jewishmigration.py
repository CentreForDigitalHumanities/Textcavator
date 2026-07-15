from datetime import datetime
import json
import logging

from django.conf import settings
from textcavator_readers.extract import Combined, JSON
import langcodes
import requests

from addcorpus.python_corpora.corpus import JSONCorpusDefinition, FieldDefinition
from addcorpus.es_mappings import int_mapping, keyword_mapping
from addcorpus.python_corpora.filters import MultipleChoiceFilter
from corpora.peaceportal.peaceportal import PeacePortal
from corpora.utils.exclude_fields import exclude_fields_without_extractor

logger = logging.getLogger('indexing')

def transform_language(language_array):
    ''' transform the language to an iso code,
    skip any languages which are not recognized by langcodes module
    TODO: we may also express the script as part of the code'''
    if not language_array:
        return None
    output = []
    for lang in language_array:
        try:
            output.append(langcodes.find(lang).to_tag())
        except:
            continue
    return output


def transform_coordinates(data):
    if data:
        return {'coordinates': data[0], 'type': data[1]}


class JewishMigration(PeacePortal, JSONCorpusDefinition):
    ''' Class for indexing Jewish Migration data '''
    title = "Modelling Jewish Migration"
    description = "Inscriptions and book entries documenting Jewish settlements in the Mediterranean"
    min_date = datetime(year=1, month=1, day=1)
    max_date = datetime(year=1800, month=12, day=31)

    data_filepath = None
    data_url = None
    data_api_key = None

    es_alias = None
    es_index = 'jewishmigration'
    image = 'jewishmigration.jpg'
    languages = ['en']

    category = 'inscription'

    def sources(self, start, end):
        if self.data_url:
            if self.data_api_key:
                headers = {"Authorization": f"Token {self.data_api_key}"}
                response = requests.get(self.data_url, headers=headers)
            else:
                response = requests.get(self.data_url)
            if response.status_code != 200:
                raise (f'Invalid response {response.status_code} from {self.data_url}')
            yield response
        elif self.data_filepath:
            with open(self.data_filepath, 'r') as f:
                list_of_sources = json.load(f)
                for source in list_of_sources:
                    yield source
        else:
            logging.getLogger('indexing').warning('No data filepath or URL provided.')

    def __init__(self):
        super().__init__()
        self._id.extractor = JSON('source')
        self.source_database.extractor = JSON('source')
        self.language.extractor = JSON('languages')
        self.language_code.extractor = JSON('languages', transform=transform_language)
        self.country.extractor = JSON('area')
        self.region.extractor = JSON('region')
        self.settlement.extractor = JSON('place_name')
        self.coordinates.extractor = Combined(
            JSON('coordinates.coordinates'),
            JSON('coordinates.type'),
            transform=transform_coordinates,
        )
        self.coordinates.visualizations = ['map']
        self.sex.extractor = JSON('sex_deceased')
        self.iconography.extractor = JSON('symbol')
        self.comments.extractor = JSON('comments')
        self.transcription.extractor = JSON('inscription')
        self.transcription_english.extractor = JSON('transcription')
        extra_fields = [
            FieldDefinition(
                name="script",
                display_name="Script",
                description="Which alphabet the source was written in",
                es_mapping=keyword_mapping(),
                extractor=JSON("scripts"),
                visualizations=["resultscount"],
            ),
            FieldDefinition(
                name="site_type",
                display_name="Site Type",
                description="Type of site where evidence for settlement was found",
                es_mapping=keyword_mapping(),
                extractor=JSON("site_type"),
            ),
            FieldDefinition(
                name="inscription_type",
                display_name="Inscription type",
                description="Type of inscription",
                es_mapping=keyword_mapping(),
                extractor=JSON("inscription_type"),
            ),
            FieldDefinition(
                name="period",
                display_name="Period",
                description="Period in which the inscription was made",
                es_mapping=keyword_mapping(),
                extractor=JSON("period"),
            ),
            FieldDefinition(
                name="estimated_centuries",
                display_name="Estimated Centuries",
                description="Estimate of centuries in which the inscription was made",
                es_mapping=keyword_mapping(),
                extractor=JSON("estimated_centuries"),
                search_filter=MultipleChoiceFilter(
                    description="Search only within these estimated centuries.",
                    option_count=4,
                ),
                visualizations=["resultscount"],
            ),
            FieldDefinition(
                name="inscription_count",
                display_name="Inscription count",
                description="Number of inscriptions",
                es_mapping=int_mapping(),
                extractor=JSON("inscriptions_count"),
            ),
            FieldDefinition(
                name="religious_profession",
                display_name="Religious profession",
                description="Religious profession of deceased",
                es_mapping=keyword_mapping(),
                extractor=JSON("religious_profession"),
            ),
            FieldDefinition(
                name="sex_dedicator",
                display_name="Gender dedicator",
                description="Gender of the dedicator",
                es_mapping=keyword_mapping(),
                extractor=JSON("sex_dedicator"),
            ),
        ]
        self.fields = [*exclude_fields_without_extractor(self.fields), *extra_fields]
