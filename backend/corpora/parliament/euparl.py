from datetime import datetime, timedelta
from functools import cache
from itertools import chain
import logging
import os
from typing import Optional, Tuple, Union

from bs4 import BeautifulSoup
from django.conf import settings
from langcodes import standardize_tag, Language
import requests
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, RDFS, RDF as RDFNS
from ianalyzer_readers.extract import Backup, Combined, JSON, Metadata, RDF, Pass

from addcorpus.es_mappings import keyword_mapping
from addcorpus.python_corpora.corpus import (
    FieldDefinition,
    JSONCorpusDefinition,
    RDFCorpusDefinition,
)
from addcorpus.python_corpora.filters import MultipleChoiceFilter
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
from corpora.utils.constants import document_context

logger = logging.getLogger('indexing')

EVENTS_METADATA = 'Events_and_structure.ttl'
MP_METADATA = 'MembersOfParliament_background.ttl'
SPEECHES = 'English.ttl'

# Namespaces of Linked Politics (NB: the purl links resolve to dead sites)
LP_EU = Namespace('http://purl.org/linkedpolitics/eu/plenary/')
LPV_EU = Namespace('http://purl.org/linkedpolitics/vocabulary/eu/plenary/')
LP = Namespace('http://purl.org/linkedpolitics/')
LPV = Namespace('http://purl.org/linkedpolitics/vocabulary/')

def add_speaker_metadata(filename: str) -> dict:
    """Parse all relevant metadata out of MembersOfParliament ttl to dict"""
    speaker_dict = {}
    speaker_graph = Graph()
    speaker_graph.parse(filename)
    speaker_subjects = speaker_graph.subjects(object=LPV.MemberOfParliament)
    for speaker in speaker_subjects:
        try:
            name = speaker_graph.value(speaker, FOAF.name).value
        except AttributeError:
            # We cannot find the name of the speaker subject
            continue
        country_node = speaker_graph.value(speaker, LPV.countryOfRepresentation)
        country_name = speaker_graph.value(country_node, RDFS.label).value
        party_list = []
        speaker_functions = speaker_graph.objects(speaker, LPV.politicalFunction)
        for function in speaker_functions:
            function_type = speaker_graph.value(function, LPV.institution)
            if speaker_graph.value(function_type, RDFNS.type) == LPV.EUParty:
                party_labels = list(speaker_graph.objects(function_type, RDFS.label))
                party_acronym = min(party_labels, key=len)
                party_name = max(party_labels, key=len)
                date_start = speaker_graph.value(function, LPV.beginning)
                date_end = speaker_graph.value(function, LPV.end)
                party_list.append({
                    'party_acronym': party_acronym,
                    'party_name': party_name,
                    'date_start': date_start.value,
                    'date_end': date_end.value
                })
        speaker_dict.update({speaker: {
            'name': name,
            'country': country_name,
            'parties': party_list
            }
        })
    return speaker_dict


def get_identifier(input_string: str) -> str:
    return input_string.split('/')[-1]


def language_name(lang_code: str) -> str:
    return Language.make(language=standardize_tag(lang_code)).display_name()


def get_speaker(input_data: Tuple[URIRef, dict]) -> str:
    (speaker, speaker_dict) = input_data
    return speaker_dict.get(speaker).get('name')


def get_speaker_country(input_data: Tuple[URIRef, dict]) -> str:
    (speaker, speaker_dict) = input_data
    return speaker_dict.get(speaker).get('country')


def get_speaker_party(input_data: Tuple[str, datetime, dict]) -> str:
    ''' look up the which EU party the speaker was part of at the date of their speech '''
    (speaker, date, party_data) = input_data
    party_list = party_data.get(speaker).get('parties')
    return next(
        (
            f"{p['party_name'].value} ({p['party_acronym'].value})"
            for p in party_list
            if (date >= p["date_start"] and date <= p["date_end"])
        ),
        None,
    )


def get_speech_index(input_data: Tuple[str, list]) -> int:
    ''' find index of speech in array of debate parts '''
    speech, speeches = input_data
    if not speech:
        return None
    return speeches.index(speech) + 1


def get_speech_text(input_string: str) -> str:
    ''' remove leading language information, e.g., `(IT)`'''
    return input_string.split(') ')[-1]


def get_uri(input_data: Union[URIRef, str]) -> str:
    ''' convert input from URIRef to string '''
    try:
        return input_data.n3().strip('<>')
    except:
        return input_data


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
            ParliamentEuropeFromRDF(),
            ParliamentEuropeFromAPI(),
        ]

    def sources(self, start, end):
        for i, subcorpus in enumerate(self.subcorpora):
            for source in subcorpus.sources(start, end):
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
    party_id = field_defaults.party_id()
    sequence = field_defaults.sequence()
    source_language = FieldDefinition(
        name='source_language',
        display_name='Source language',
        description='Original language of the speech',
        es_mapping=keyword_mapping(),
        search_filter=MultipleChoiceFilter(
            description='Search only in speeches in the selected original languages',
            option_count=50,
        ),
        visualizations=['resultscount', 'termfrequency'],
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
    speech = field_defaults.speech(language='en')
    speech_id = field_defaults.speech_id()
    url = field_defaults.url()

    def __init__(self):
        self.fields = [
            self.date,
            self.debate_id,
            self.debate_title,
            self.party,
            self.party_id,
            self.sequence,
            self.source_language,
            self.speaker,
            self.speaker_country,
            self.speaker_id,
            self.speech,
            self.speech_id,
            self.url,
        ]


def api_convert_xml(speech_xml: str) -> str:
    speech_soup = BeautifulSoup(speech_xml, 'lxml')
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
    soup = BeautifulSoup(response.content, 'lxml')
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
    return party_response.json().get('data')[0].get('prefLabel').get('en')

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

    def sources(self, start, end, **kwargs):
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

    source_language = field_defaults.language()
    source_language.name = 'source_language'
    source_language.extractor = JSON("originalLanguage", transform=api_get_language)

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

    fields = [
        date,
        debate_id,
        debate_title,
        party,
        party_id,
        sequence,
        source_language,
        speaker,
        speaker_country,
        speaker_id,
        speech,
        speech_id,
    ]


class ParliamentEuropeFromRDF(RDFCorpusDefinition):
    """
    Speeches of the European parliament, originally in or translated to English,
    provided as Linked Open Data by the "Talk of Europe" project
    """

    min_date = datetime(year=1999, month=7, day=20)
    max_date = datetime(year=2017, month=7, day=6)

    data_directory = settings.PP_EUPARL_DATA

    def sources(self, start, end, **kwargs):
        metadata = {
            "speakers": add_speaker_metadata(
                os.path.join(self.data_directory, MP_METADATA)
            )
        }
        yield os.path.join(self.data_directory, SPEECHES), metadata

    def document_subjects(self, graph: Graph):
        """return all subjects which have either translated or spoken text"""
        return chain(
            graph.subjects(predicate=LPV.translatedText),
            graph.subjects(predicate=LPV.spokenText),
        )

    def data_from_file(self, filename: str) -> Graph:
        '''we combine the graphs in place, to keep memory load low'''
        graph = Graph()
        graph.parse(filename)
        graph.parse(os.path.join(self.data_directory, EVENTS_METADATA))
        return graph

    date = field_defaults.date(min_date, max_date)
    date.extractor = RDF(DCTERMS.date, transform=lambda x: x.strftime('%Y-%m-%d'))

    debate_id = field_defaults.debate_id()
    debate_id.extractor = RDF(DCTERMS.isPartOf, transform=get_identifier)

    debate_title = field_defaults.debate_title()
    debate_title.extractor = RDF(DCTERMS.isPartOf, DCTERMS.title)

    party = field_defaults.party()
    party.extractor = Combined(
        RDF(LPV.speaker),
        RDF(DCTERMS.date),
        Metadata('speakers'),
        transform=get_speaker_party,
    )

    sequence = field_defaults.sequence()
    sequence.extractor = Combined(
        RDF(),
        RDF(DCTERMS.isPartOf, DCTERMS.hasPart, multiple=True),
        transform=get_speech_index,
    )

    source_language = field_defaults.language()
    source_language.name = 'source_language'
    source_language.extractor = RDF(DCTERMS.language, transform=language_name)

    speaker = field_defaults.speaker()
    speaker.extractor = Combined(
        RDF(LPV.speaker), Metadata('speakers'), transform=get_speaker
    )

    speaker_country = FieldDefinition(
        name='speaker_country',
        extractor=Combined(
            RDF(LPV.speaker), Metadata('speakers'), transform=get_speaker_country
        ),
    )

    speech = field_defaults.speech(language='en')
    speech.extractor = Backup(
        RDF(
            LPV.spokenText,
        ),
        RDF(
            LPV.translatedText,
        ),
        transform=get_speech_text,
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = RDF(transform=get_identifier)

    url = field_defaults.url()
    url.extractor = Backup(RDF(LPV.videoURI, transform=get_uri), RDF(transform=get_uri))

    fields = [
        date,
        debate_id,
        debate_title,
        party,
        sequence,
        source_language,
        speaker,
        speaker_country,
        speech,
        speech_id,
        url,
    ]
