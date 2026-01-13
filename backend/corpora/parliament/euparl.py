from datetime import datetime, timedelta
from functools import cache
import logging
import os
from typing import Optional

from bs4 import BeautifulSoup
from django.conf import settings
from langcodes import standardize_tag, Language
import requests
from ianalyzer_readers.extract import Combined, JSON, Metadata, Pass, CSV, Constant
from ianalyzer_readers.readers.core import Field

from addcorpus.es_mappings import keyword_mapping, main_content_mapping
from addcorpus.python_corpora.corpus import (
    FieldDefinition,
    JSONCorpusDefinition,
)
from addcorpus.python_corpora.filters import MultipleChoiceFilter
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
from corpora.utils.constants import document_context
from corpora.parliament.utils.rds_reader import RDSReader

logger = logging.getLogger('indexing')


def language_name(lang_code: str) -> str:
    return Language.make(language=standardize_tag(lang_code)).display_name()


class ParliamentEurope(Parliament):
    title = 'People & Parliament (European Parliament)'
    description = "Speeches from the European Parliament (EP)"
    es_index = getattr(settings, 'PP_EUPARL_INDEX', 'parliament-euparl')
    data_directory = settings.PP_EUPARL_DATA
    languages = ['en']
    category = "parliament"
    document_context = document_context()
    description_page = 'euparl.md'
    image = 'euparl.jpeg'
    min_date = datetime(year=1999, month=7, day=20)
    max_date = datetime.now()

    @property
    def subcorpora(self):
        return [
            EUPDCorpReader(),
            ParliamentEuropeFromAPI(),
        ]

    def sources(self, **kwargs):
        for i, subcorpus in enumerate(self.subcorpora):
            logger.info(f'Extracting subcorpus: {subcorpus.__class__.__name__}')
            for source in subcorpus.sources(**kwargs):
                filename, metadata = source
                metadata["subcorpus"] = i
                yield filename, metadata

    def source2dicts(self, source, **kwargs):
        filename, metadata = source

        subcorpus_index = metadata["subcorpus"]
        subcorpus = self.subcorpora[subcorpus_index]

        docs = subcorpus.source2dicts(source)
        for doc in docs:
            yield {field.name: doc.get(field.name, None) for field in self.fields}

    debate_id = field_defaults.debate_id()
    debate_title = field_defaults.debate_title()
    date = field_defaults.date(min_date, max_date)
    party = field_defaults.party()
    party_full = field_defaults.party_full()
    party_id = field_defaults.party_id()
    party_national = FieldDefinition(
        name='party_national',
        display_name='National party',
        es_mapping=keyword_mapping(enable_full_text_search=True),
    )
    sequence = field_defaults.sequence()
    original_language = field_defaults.language()
    original_language.name = 'original_language'
    original_language.display_name='Original language'
    original_language.description = 'Original language of the speech'

    speaker = field_defaults.speaker()
    speaker_id = field_defaults.speaker_id()
    speaker_country = FieldDefinition(
        name='speaker_country',
        display_name='Represented country',
        description='The EU country the speaker represents',
        es_mapping=keyword_mapping(),
        search_filter=MultipleChoiceFilter(
            description='Search in speeches of speakers from specific countries',
            option_count=50,
        ),
        visualizations=['resultscount', 'termfrequency'],
    )
    speaker_gender = field_defaults.speaker_gender()
    speaker_birth_year = field_defaults.speaker_birth_year()
    speech = field_defaults.speech(language='en')
    speech.description = 'Speech translated to English'
    speech_original = FieldDefinition(
        name='speech_original',
        display_name='Original speech',
        description='Speech in the original language',
        es_mapping=main_content_mapping(),
    )
    speech_id = field_defaults.speech_id()
    url = field_defaults.url()
    source_archive = field_defaults.source_archive()

    def __init__(self):
        self.fields = [
            self.date,
            self.debate_id,
            self.debate_title,
            self.original_language,
            self.party,
            self.party_full,
            self.party_id,
            self.party_national,
            self.sequence,
            self.speaker,
            self.speaker_country,
            self.speaker_gender,
            self.speaker_birth_year,
            self.speaker_id,
            self.speech,
            self.speech_original,
            self.speech_id,
            self.url,
            self.source_archive,
        ]


def api_convert_xml(speech_xml: str) -> str:
    speech_soup = BeautifulSoup(speech_xml, 'lxml-xml')
    return speech_soup.find('speech').find('p').text


def api_get_language(languages: list[str]) -> str:
    language = language_name(languages[0].split('/')[-1])
    return language


def api_get_speaker_id(participant: str) -> str:
    return participant.split('/')[-1]


@cache
def api_get_preflabel(url: str) -> Optional[str]:
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content, 'lxml-xml')
    return soup.find('skos:preflabel', {'xml:lang': 'en'}).text


@cache
def api_get_speaker_info(participant: str) -> dict:
    '''Query metadata about the speaker, unless it's already been queried before'''
    speaker_id = api_get_speaker_id(participant)
    speaker_response = requests.get(
        f'https://data.europarl.europa.eu/api/v2/meps/{speaker_id}?format=application%2Fld%2Bjson'
    )
    if not speaker_response.status_code == 200:
        logger.warning(f"No response for {speaker_id}")
        return {}
    else:
        return speaker_response.json().get('data')[0]


def api_get_speaker_country(participant: str) -> Optional[str]:
    speaker_metadata = api_get_speaker_info(participant)
    citizenship = speaker_metadata.get('citizenship')
    return api_get_preflabel(citizenship)


def api_get_speaker_name(participant: str) -> str:
    speaker_metadata = api_get_speaker_info(participant)
    given_name = speaker_metadata.get('givenName')
    family_name = speaker_metadata.get('familyName')
    return f'{given_name} {family_name}'


@cache
def api_get_party_id(data) -> dict:
    participant, date = data
    speaker_metadata = api_get_speaker_info(participant)
    memberships = speaker_metadata.get('hasMembership')
    for membership in memberships:
        if (
            membership.get('membershipClassification')
            != 'def/ep-entities/EU_POLITICAL_GROUP'
        ):
            continue
        membership_period = membership.get('memberDuring')
        end_date = membership_period.get('endDate', datetime.now().strftime('%Y-%m-%d'))
        if membership_period.get('startDate') <= date <= end_date:
            return membership.get('organization').split('/')[-1]
    return ''


def api_get_party_name(data) -> Optional[str]:
    party_id = api_get_party_id(data)
    return api_get_party_name_from_id(party_id)


@cache
def api_get_party_name_from_id(party_id: str) -> str:
    if not party_id:
        return None
    party_response = requests.get(
        f'https://data.europarl.europa.eu/api/v2/corporate-bodies/{party_id}?format=application%2Fld%2Bjson&language=en'
    )
    if party_response.status_code != 200:
        return None
    return party_response.json().get('data')[0].get('label')


def _api_get_party_full_name(data) -> Optional[str]:
    party_id = api_get_party_id(data)
    return _api_get_party_full_name_from_id(party_id)


@cache
def _api_get_party_full_name_from_id(party_id: str) -> str:
    if not party_id:
        return None
    party_response = requests.get(
        f'https://data.europarl.europa.eu/api/v2/corporate-bodies/{party_id}?format=application%2Fld%2Bjson&language=en'
    )
    if party_response.status_code != 200:
        return None
    return party_response.json().get('data')[0].get('altLabel').get('en')


def first(values):
    if len(values):
        return values[0]

class ParliamentEuropeFromAPI(JSONCorpusDefinition):
    """
    Speeches of the European parliament, originally in or translated to English,
    provided through the Europarl Open Data API
    """

    min_date = datetime(year=2024, month=7, day=7)
    max_date = datetime.now()

    # Variables to hold interim metadata
    speaker_metadata = {}
    party_metadata = {}
    record_path = ['data', 'recorded_in_a_realization_of']
    meta = [
        ['data', 'had_participation', 'had_participant_person'],
        ['data', 'activity_id'],
    ]

    def sources(self, **kwargs):
        date = self.min_date
        while date < self.max_date:
            date += timedelta(days=1)
            formatted_date = date.strftime('%Y-%m-%d')
            meeting_id = f'MTG-PL-{formatted_date}'
            response = requests.get(
                f'https://data.europarl.europa.eu/api/v2/meetings/{meeting_id}/activities?format=application%2Fld%2Bjson',
                headers={'accept': 'application/ld+json'},
            )
            if response.status_code != 200:
                continue
            meeting_data = response.json().get('data')
            metadata = {'date': formatted_date}
            for event in meeting_data:
                if event.get("had_activity_type") != "def/ep-activities/PLENARY_DEBATE":
                    continue
                metadata['debate_id'] = event.get('activity_id')
                metadata['debate_title'] = event.get('activity_label').get('en')

                sequence_in_debate = 0

                for speech in event.get('consists_of'):
                    speech_id = speech.split("/")[-1]
                    speech_response = requests.get(
                        f'https://data.europarl.europa.eu/api/v2/speeches/{speech_id}?include-output=xml_fragment&language=en&format=application%2Fld%2Bjson'
                    )
                    if speech_response.status_code != 200:
                        continue
                    sequence_in_debate += 1
                    metadata['sequence'] = sequence_in_debate
                    yield speech_response, metadata

    def iterate_data(self, data: Dict, metadata):
        speeches_with_speaker = [
            item for item in data['data']
            if 'had_participation' in item
        ]
        filtered_data = data | { 'data': speeches_with_speaker}
        return super().iterate_data(filtered_data, metadata)

    debate_id = field_defaults.debate_id()
    debate_id.extractor = Metadata('debate_id')

    debate_title = field_defaults.debate_title()
    debate_title.extractor = Metadata('debate_title')

    date = field_defaults.date(min_date, max_date)
    date.extractor = Metadata('date')

    party = field_defaults.party()
    party.extractor = Combined(
        JSON(
            "data.had_participation.had_participant_person",
            transform=first,
        ),
        Metadata('date'),
        transform=api_get_party_name,
    )

    party_full = field_defaults.party_full()
    party_full.extractor = Combined(
        JSON(
            "data.had_participation.had_participant_person",
            transform=first,
        ),
        Metadata('date'),
        transform=_api_get_party_full_name,
    )

    party_id = field_defaults.party_id()
    party_id.extractor = Combined(
        JSON(
            "data.had_participation.had_participant_person",
            transform=first
        ),
        Metadata('date'),
        transform=api_get_party_id,
    )

    sequence = field_defaults.sequence()
    sequence.extractor = Metadata('sequence')

    original_language = field_defaults.language()
    original_language.name = 'original_language'
    original_language.extractor = JSON("originalLanguage", transform=api_get_language)

    speaker = field_defaults.speaker()
    speaker.extractor = Pass(
            JSON(
            "data.had_participation.had_participant_person",
            transform=first,
        ),
        transform=api_get_speaker_name,
    )

    speaker_country = FieldDefinition(
        name='speaker_country',
        extractor=Pass(
            JSON(
                "data.had_participation.had_participant_person",
                transform=first,
            ),
            transform=api_get_speaker_country,
        ),
    )

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = Pass(
        JSON(
            "data.had_participation.had_participant_person",
            transform=first,
        ),
        transform=api_get_speaker_id,
    )

    speech = field_defaults.speech()
    speech.extractor = JSON(
        "api:xmlFragment.en",
        transform=api_convert_xml,
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = JSON("data.activity_id")

    source_archive = field_defaults.source_archive()
    source_archive.extractor = Constant('Europarl Open Data')

    fields = [
        date,
        debate_id,
        debate_title,
        party,
        party_full,
        party_id,
        sequence,
        original_language,
        speaker,
        speaker_country,
        speaker_id,
        speech,
        speech_id,
        source_archive,
    ]


def _to_int(value) -> Optional[int]:
    if value or value == 0:
        return int(value)

def _format_name(values) -> str:
    return ' '.join(
        value for value in filter(None, values)
    )

class EUPDCorpReader(RDSReader):
    data_directory = settings.PP_EUPARL_DATA

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            if filename.lower().endswith('.rds'):
                yield os.path.join(self.data_directory, filename), {}

    fields = [
        Field(
            name='date',
            extractor=CSV('date'),
        ),
        Field(
            name='debate_id',
            extractor=CSV('file'),
        ),
        Field(
            name='debate_title',
            extractor=CSV('agenda'),
        ),
        Field(
            name='original_language',
            extractor=CSV(
                'language',
                transform=lambda value: language_name(value.lower()),
            ),
        ),
        Field(
            name='party',
            extractor=CSV('epg_short'),
        ),
        Field(
            name='party_full',
            extractor=CSV('epg_long'),
        ),
        Field(
            name='party_national',
            extractor=CSV('party_name'),
        ),
        Field(
            name='sequence',
            extractor=CSV('doc_id', transform=int),
        ),
        Field(
            name='speech',
            extractor=CSV('speech_en'),
        ),
        Field(
            name='speech_original',
            extractor=CSV('speech'),
        ),
        Field(
            name='speaker',
            extractor=Combined(
                CSV('firstname'),
                CSV('lastname'),
                transform=_format_name,
            )
        ),
        Field(
            name='speaker_id',
            extractor=Pass(
                CSV('mepid', transform=_to_int),
                transform=str,
            ),
        ),
        Field(
            name='speaker_gender',
            extractor=CSV(
                'gender',
                transform=lambda value: 'Male' if value else 'Female',
            )
        ),
        Field(
            name='speaker_birth_year',
            extractor=CSV('birth_year', transform=_to_int)
        ),
        Field(
            name='speaker_country',
            extractor=CSV('nationality'),
        ),
        Field(
            name='source_archive',
            extractor=Constant('EUPDCorp'),
        )
    ]
