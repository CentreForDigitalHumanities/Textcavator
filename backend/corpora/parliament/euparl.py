from datetime import datetime, timedelta
from functools import cache
import logging
import os
from typing import Optional, Dict, List, Tuple, Union
from urllib import parse
import math
import numbers

from bs4 import BeautifulSoup
from django.conf import settings
from langcodes import standardize_tag, Language
import requests
from ianalyzer_readers.extract import Combined, JSON, Metadata, Pass, CSV, Constant
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.readers.json import JSONReader

from addcorpus.es_mappings import keyword_mapping, main_content_mapping
from addcorpus.python_corpora.corpus import FieldDefinition
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
    max_date = getattr(settings, 'PP_EUPARL_MAX_DATE', datetime.now())
    language_field = 'original_language_code'

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
        search_filter=MultipleChoiceFilter(),
        visualizations=['resultscount', 'termfrequency'],
    )
    sequence = field_defaults.sequence()
    original_language = field_defaults.language()
    original_language.name = 'original_language'
    original_language.display_name='Original language'
    original_language.description = 'Original language of the speech'

    original_language_code = FieldDefinition(
        name='original_language_code',
        es_mapping=keyword_mapping(),
        hidden=True,
    )

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
    speech.language = 'en'

    speech_original = FieldDefinition(
        name='speech_original',
        display_name='Original speech',
        description='Speech in the original language',
        es_mapping=main_content_mapping(),
        search_field_core=True,
        display_type='text_content',
        language='dynamic',
    )

    speech_id = field_defaults.speech_id()
    source_archive = FieldDefinition(
        name='source_archive',
        display_name='Source archive',
        description='Source dataset for this document',
        es_mapping=keyword_mapping(),
    )

    def __init__(self):
        self.fields = [
            self.date,
            self.debate_id,
            self.debate_title,
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
            self.original_language,
            self.original_language_code,
            self.speech_id,
            self.source_archive,
        ]


def _api_url(path: str, query: Dict = dict()) -> str:
    full_path = parse.urljoin('/api/v2/', path)
    base_query = {
        'format': 'application/ld+json',
        'User-Agent': 'textcavator',
    }
    query_string = parse.urlencode(base_query | query)
    url = parse.urlunsplit(['https', 'data.europarl.europa.eu', full_path, query_string, ''])
    return url


def api_convert_xml(speech_xml: str) -> str:
    speech_soup = BeautifulSoup(speech_xml, 'lxml-xml')
    paragraphs = speech_soup.find_all('p')
    return '\n\n'.join(p.text for p in paragraphs)


def api_get_language(languages: List[str]) -> Optional[str]:
    label, _ = _api_get_language_data(languages[0])
    return label

def _api_get_language_code(languages: List[str]):
    _, code = _api_get_language_data(languages[0])
    return code

@cache
def _api_get_language_data(url: str) -> Tuple[str, str] | Tuple[None, None]:
    response = requests.get(url)
    if response.status_code != 200:
        return None, None
    soup = BeautifulSoup(response.content, 'lxml-xml')
    label = soup.find('skos:prefLabel', {'xml:lang': 'en'}).text
    code = soup.find('skos:notation', {'rdf:datatype': 'http://publications.europa.eu/ontology/euvoc#ISO_639_1'}).text
    return label, code

def api_get_speaker_id(participant: str) -> str:
    return participant.split('/')[-1]


@cache
def api_get_preflabel(url: str) -> Optional[str]:
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content, 'lxml-xml')
    return soup.find('skos:prefLabel', {'xml:lang': 'en'}).text



@cache
def api_get_speaker_info(participant: str) -> Optional[Dict]:
    '''Query metadata about the speaker, unless it's already been queried before'''
    speaker_id = api_get_speaker_id(participant)
    speaker_url = _api_url(f'meps/{speaker_id}')
    speaker_response = requests.get(speaker_url)
    if not speaker_response.status_code == 200:
        logger.warning(f"No response for person {speaker_id}")
        return {}
    else:
        return speaker_response.json().get('data')[0]


def api_get_speaker_country(participant: str) -> Optional[str]:
    speaker_metadata = api_get_speaker_info(participant)
    citizenship = speaker_metadata.get('citizenship')
    if citizenship:
        return api_get_preflabel(citizenship)


def _api_get_speaker_gender(participant: str) -> Optional[str]:
    speaker_metadata = api_get_speaker_info(participant)
    gender_uri = speaker_metadata.get('hasGender')
    if gender_uri:
        return gender_uri.split('/')[-1].title()

def _api_get_speaker_birth_year(participant: str) -> Optional[int]:
    speaker_metadata = api_get_speaker_info(participant)
    birth_date = speaker_metadata.get('bday')
    if birth_date:
        d = datetime.strptime(birth_date, '%Y-%m-%d')
        return d.year

def api_get_speaker_name(participant: str) -> str:
    speaker_metadata = api_get_speaker_info(participant)
    given_name = speaker_metadata.get('givenName')
    family_name = speaker_metadata.get('familyName')
    if given_name or family_name:
        return f'{given_name} {family_name}'


@cache
def api_get_party_id(data: Tuple[str, datetime]) -> dict:
    participant, date = data
    return _api_select_party(participant, date, 'def/ep-entities/EU_POLITICAL_GROUP')

def _api_select_party(participant: str, date: datetime, classification: str) -> Optional[str]:
    speaker_metadata = api_get_speaker_info(participant)
    memberships = speaker_metadata.get('hasMembership') or []
    for membership in memberships:
        if membership.get('membershipClassification') != classification:
            continue
        membership_period = membership.get('memberDuring')
        end_date = membership_period.get('endDate', datetime.now().strftime('%Y-%m-%d'))
        if membership_period.get('startDate') <= date <= end_date:
            return membership.get('organization').split('/')[-1]

def _api_get_national_party_id(data: Tuple[str, datetime]) -> Optional[str]:
    participant, date = data
    return _api_select_party(participant, date, 'def/ep-entities/NATIONAL_POLITICAL_GROUP')


def api_get_party_name(data) -> Optional[str]:
    party_id = api_get_party_id(data)
    return api_get_party_name_from_id(party_id)

def _api_get_national_party_name(data: Tuple[str, datetime]) -> Optional[str]:
    party_id = _api_get_national_party_id(data)
    return api_get_party_name_from_id(party_id, False)

_party_name_replacements = {
    'The Left': 'GUENGL',
    'Verts/ALE': 'GEFA',
    'S&D': 'SOCPESPASD',
}
'Replaces some party labels with the ones used in the 1999-2024 datasets'

@cache
def api_get_party_name_from_id(party_id: str, replacements=True) -> str:
    data = _api_get_party_metadata(party_id)
    if data:
        label = data.get('data')[0].get('label')
        if replacements:
            return _party_name_replacements.get(label, label)
        return label


def _api_get_party_full_name(data) -> Optional[str]:
    party_id = api_get_party_id(data)
    return _api_get_party_full_name_from_id(party_id)


@cache
def _api_get_party_full_name_from_id(party_id: str) -> str:
    data = _api_get_party_metadata(party_id)
    if data:
        return data.get('data')[0].get('altLabel').get('en')

@cache
def _api_get_party_metadata(party_id: str) -> Dict:
    if not party_id:
        return None
    party_url = _api_url(f'corporate-bodies/{party_id}', {'language': 'en'})
    party_response = requests.get(party_url)
    if party_response.status_code != 200:
        return None
    return party_response.json()

def _api_speech_key(language_code: str):
    return f'api:xmlFragment.{language_code}'


def _api_get_original_speech(data):
    _, code = _api_get_language_data(data['originalLanguage'][0])
    return data.get(_api_speech_key(code))


def first(values):
    if len(values):
        return values[0]

class _JSON(JSON):
    '''
    Edited JSON extractor that also accepts 0 keys to return the object as-is
    '''
    # TODO: make this change in ianalyzer_readers

    def _apply(self, data: Union[str, dict], key_index: int = 0, **kwargs):
        if not len(self.keys):
            return data
        return super()._apply(data, key_index, **kwargs)


class ParliamentEuropeFromAPI(JSONReader):
    """
    Reader to extract speeches from the Europarl Open Data API

    Extracts from 9/2/2024 until the present.
    """

    min_date = datetime(year=2024, month=2, day=9)
    max_date = datetime.now()

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
            meeting_url = _api_url(f'meetings/{meeting_id}/activities')
            response = requests.get(
                meeting_url,
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
                    speech_url = _api_url(f'speeches/{speech_id}', {'include-output': 'xml_fragment'})
                    speech_response = requests.get(speech_url)
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
        records = list(super().iterate_data(filtered_data, metadata))
        filtered_records = [
            record for record in records
            if record['data'].get(_api_speech_key('en'))
        ]
        return filtered_records

    fields = [
        Field(
            name='debate_id',
            extractor=Metadata('debate_id'),
        ),
        Field(
            name='debate_title',
            extractor=Metadata('debate_title'),
        ),
        Field(
            name='date',
            extractor=Metadata('date')
        ),
        Field(
            name='party',
            extractor=Combined(
                JSON(
                    "data.had_participation.had_participant_person",
                    transform=first,
                ),
                Metadata('date'),
                transform=api_get_party_name,
            )
        ),
        Field(
            name='party_full',
            extractor=Combined(
                JSON(
                    "data.had_participation.had_participant_person",
                    transform=first,
                ),
                Metadata('date'),
                transform=_api_get_party_full_name,
            )
        ),
        Field(
            name='party_id',
            extractor=Combined(
                JSON(
                    "data.had_participation.had_participant_person",
                    transform=first
                ),
                Metadata('date'),
                transform=api_get_party_id,
            )
        ),
        Field(
            name='party_national',
            extractor=Combined(
                JSON(
                    "data.had_participation.had_participant_person",
                    transform=first
                ),
                Metadata('date'),
                transform=_api_get_national_party_name,
            )
        ),
        Field(
            name='sequence',
            extractor=Metadata('sequence')
        ),
        Field(
            name='original_language',
            extractor=JSON("originalLanguage", transform=api_get_language)
        ),
        Field(
            name='original_language_code',
            extractor=JSON('originalLanguage', transform=_api_get_language_code)
        ),
        Field(
            name='speaker',
            extractor=Pass(
                    JSON(
                    "data.had_participation.had_participant_person",
                    transform=first,
                ),
                transform=api_get_speaker_name,
            )
        ),
        Field(
            name='speaker_country',
            extractor=Pass(
                JSON(
                    "data.had_participation.had_participant_person",
                    transform=first,
                ),
                transform=api_get_speaker_country,
            ),
        ),
        Field(
            name='speaker_gender',
            extractor=Pass(
                JSON(
                    'data.had_participation.had_participant_person',
                    transform=first,
                ),
                transform=_api_get_speaker_gender,
            )
        ),
        Field(
            name='speaker_birth_year',
            extractor=Pass(
                JSON(
                    'data.had_participation.had_participant_person',
                    transform=first,
                ),
                transform=_api_get_speaker_birth_year,
            )
        ),
        Field(
            name='speaker_id',
            extractor=Pass(
                JSON(
                    "data.had_participation.had_participant_person",
                    transform=first,
                ),
                transform=api_get_speaker_id,
            )
        ),
        Field(
            name='speech',
            extractor=JSON(
                _api_speech_key('en'),
                transform=api_convert_xml,
            )
        ),
        Field(
            name='speech_original',
            extractor=Pass(
                _JSON(
                    transform=_api_get_original_speech
                ),
                transform=api_convert_xml,
            )
        ),
        Field(
            name='id',
            extractor=JSON("data.activity_id")
        ),
        Field(
            name='source_archive',
            extractor=Constant('European Parliament Open Data API')
        ),
    ]


def _to_int(value) -> Optional[int]:
    if (value or value == 0) and not math.isnan(value):
        return int(value)

def _format_name(values) -> str:
    return ' '.join(
        value for value in filter(None, values)
    )

def _nan_to_none(value):
    if not isinstance(value, numbers.Number) or not math.isnan(value):
        return value

def _format_gender(value):
    if value == 1:
        return 'Male'
    if value == 0:
        return 'Female'


class EUPDCorpReader(RDSReader):
    '''
    Reader for the EUPDCorp dataset. Contains debates from 20/7/1999 to 8/2/2024
    '''

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
            name='original_language_code',
            extractor=CSV('language', transform=lambda value: value.lower())
        ),
        Field(
            name='party',
            extractor=CSV('epg_short', transform=_nan_to_none),
        ),
        Field(
            name='party_full',
            extractor=CSV('epg_long', transform=_nan_to_none),
        ),
        Field(
            name='party_national',
            extractor=CSV('party_name', transform=_nan_to_none),
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
            extractor=CSV('gender', transform=_format_gender)
        ),
        Field(
            name='speaker_birth_year',
            extractor=CSV('birth_year', transform=_to_int)
        ),
        Field(
            name='speaker_country',
            extractor=CSV('nationality', transform=_nan_to_none),
        ),
        Field(
            name='source_archive',
            extractor=Constant('EUPDCorp'),
        )
    ]
