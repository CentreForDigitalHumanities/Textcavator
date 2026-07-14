import os
from datetime import datetime
from glob import glob
import re
from bs4 import BeautifulSoup
from pathlib import Path, PurePath
import json

from django.conf import settings

from ianalyzer_readers.xml_tag import Tag
from ianalyzer_readers.extract import Constant, XML, Metadata, Cache, Combined


from addcorpus.python_corpora.corpus import XMLCorpusDefinition, FieldDefinition
from addcorpus.python_corpora.filters import MultipleChoiceFilter
from addcorpus.es_mappings import keyword_mapping, text_mapping, date_mapping, main_content_mapping
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
from corpora.utils.constants import document_context



def extract_date(path: str):
    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    if date_pattern.search(path):
        return date_pattern.search(path).group(0)
    else:
        return None

def extract_chamber(path: str):
    if 'daylord' in path:
        return 'House of Lords'
    elif 'debates' in path:
        return 'House of Commons'
    else:
        return None
    
def generate_title(chamber: str, date: str):
    return "{} Debate on {}".format(chamber, date)

def extract_debate_id(path):
    id_pattern = re.compile(r"\D{7}\d{4}-\d{2}-\d{2}\D")
    if id_pattern.search(path):
        return id_pattern.search(path).group(0)
    else:
        return None

def abbreviate_speech_id(full_id):
    '''
    full speech id: uk.org.publicwhip/debate/2022-01-05c.10.6
    abbreviated id: 10.6
    '''
    return '.'.join(full_id.split('.')[-2:])

def extract_topics_and_subtopics(path):
    with open(path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, "lxml")
    
    topics = {}
    subtopics = {}
    for tag in soup.find_all('major-heading'):
        topics[abbreviate_speech_id(tag['id'])] = tag.text.replace('\n', '')
    
    for tag in soup.find_all('minor-heading'):
        subtopics[abbreviate_speech_id(tag['id'])] = tag.text.replace('\n', '')

    return topics, subtopics

def extract_speaker_ids(path):
    with open(path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, "lxml")
    
    speaker_ids = []
    for tag in soup.find_all('speech'):
        if tag.has_attr('person_id'):
            if tag.attrs['person_id'].split('/')[-1] not in speaker_ids:
                speaker_ids.append(tag.attrs['person_id'].split('/')[-1])

    return speaker_ids

def select_topic(input):
        full_speech_id, topic_dict = input
        speech_id = abbreviate_speech_id(full_speech_id)
        previous_topic = ''
        for key in topic_dict:
            if float(key) > float(speech_id):
                return previous_topic
            else:
                previous_topic = topic_dict[key]

def lookup_person_attribute(lookup_tuple):
    metadata_dict, id, name, label = lookup_tuple #name is only included for debugging purposes

    id = id.split('/')[-1] if id else None # twfy ID is at the end of uri 
    if id in metadata_dict and label in metadata_dict[id]:
        return metadata_dict[id][label]
    else:
        return None

def lookup_person_atttribute_date(lookup_tuple):
    date_string = lookup_person_attribute(lookup_tuple)
    if date_string:
        return date_string[:10]
    else:
        return None
    
def find_current_positions(metadata_dict, date):
    current_positions = {}
    for person in metadata_dict:
        current_position_list = []
        for position in metadata_dict[person]['positions']:
            if 'startTime' in position and 'endTime' in position:
                try:
                    date_range = (datetime.strptime(position['startTime'][:10], "%Y-%m-%d"), 
                                datetime.strptime(position['endTime'][:10], "%Y-%m-%d"))
                except ValueError:
                    continue #disregard missing dates
                if date_range[0] < datetime.strptime(date, "%Y-%m-%d") < date_range[1]:
                    current_position_list.append(position)
            elif 'startTime' in position:
                current_position_list.append(position)
        current_positions[person] = current_position_list
    return current_positions


def lookup_current_ministerial_position(lookup_tuple):
    positions_dict, id, name = lookup_tuple
    id = id.split('/')[-1] if id else None
    if id in  positions_dict:
        for position in positions_dict[id]:
            if position['minister']:
                return position['positionLabel']
    return None

def get_current_positions(positions_dict, id):
    id = id.split('/')[-1] if id else None
    if id and id in positions_dict:
        return positions_dict[id]
    else:
        return []


def lookup_current_parliamentary_position(lookup_tuple):
    positions_dict, id, name = lookup_tuple
    current_positions = get_current_positions(positions_dict, id)
    for position in current_positions:
        if position['member_parliament']:
            return position['positionLabel']
    return None

def lookup_current_party(lookup_tuple):
    positions_dict, id, name = lookup_tuple
    current_positions = get_current_positions(positions_dict, id)
    if current_positions:
        for position in current_positions:
            if 'partyLabel' in position:
                return position['partyLabel']
            elif 'partyBackupLabel' in position:
                return position['partyBackupLabel']
            else:
                continue
    else:
        return None

class ParliamentUKNew(Parliament, XMLCorpusDefinition):
    title = 'Talking Empire (UK 2022-2025)'
    description = "Speeches from the House of Lords and House of Commons (2022-2025)"
    data_directory = settings.TE_UK_NEW_DATA
    min_date = datetime(year=2022, month=1, day=1)
    max_date = datetime(year=2025, month=12, day=31)
    es_index = getattr(settings, 'TE_UK_NEW_ES_INDEX', 'parliament-uk-new')
    image = 'uk.jpeg'
    # word_model_path = getattr(settings, 'TE_UK_NEW_WM', None) ## TODO: add word model?
    languages = ['en']
    description_page = 'uk-new.md'
    field_entry = 'speech_id'
    document_context = document_context()

    tag_toplevel = Tag("publicwhip")
    tag_entry = Tag("speech")

    def sources(self, start: datetime, end: datetime):
        metadata = {}
        with open(os.path.join(self.data_directory, 'merged_metadata_twfy_keys.json'), 'r', encoding='utf-8') as file:
             all_person_metadata = json.load(file)

        for directory in [dir for dir in Path(self.data_directory).iterdir() if dir.is_dir()]:
            for xml_file in glob('*.xml', root_dir=directory):
                full_path = self.data_directory / directory / xml_file
                metadata['date'] = extract_date(xml_file)
                metadata['chamber'] = extract_chamber(xml_file)
                metadata['debate_title'] = generate_title(metadata['chamber'], metadata['date'])
                metadata['debate_id'] = extract_debate_id(xml_file)
                metadata['topics'], metadata['subtopics'] = extract_topics_and_subtopics(full_path)
                metadata['speaker_ids'] = extract_speaker_ids(full_path)
                metadata['speaker_metadata'] = {}
                for id in metadata['speaker_ids']:
                    if id in all_person_metadata:
                        metadata['speaker_metadata'][id] = all_person_metadata[id]
                metadata['current_positions'] = find_current_positions(metadata['speaker_metadata'], metadata['date'])

                yield str(full_path), metadata
        
    _speech_id_extractor = Cache(XML(attribute='id'))
    
    chamber = field_defaults.chamber()
    chamber.extractor = Metadata('chamber')

    country = field_defaults.country()
    country.extractor = Constant(
        value='United Kingdom'
    )

    date = field_defaults.date()
    date.extractor = Metadata('date')

    debate_title = field_defaults.debate_title()
    debate_title.extractor = Metadata('debate_title')
    debate_title.language = 'en'

    debate_id = field_defaults.debate_id()
    debate_id.extractor = Metadata('debate_id')

    speech = field_defaults.speech(language='en')
    speech.extractor = XML(
        Tag("p"),
        flatten=True
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = XML(
        attribute='id'
    )

    speaker = field_defaults.speaker()
    speaker.extractor = XML(
        attribute='speakername'
    )
    speaker.search_filter = MultipleChoiceFilter(
            description='Search only in debates from the selected chamber(s)',
            option_count=9001,
        )

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = XML(
        attribute='person_id'
    )

    speaker_gender = field_defaults.speaker_gender()
    speaker_gender.extractor = Combined(
        Metadata('speaker_metadata'),
        XML(attribute='person_id'),
        XML(attribute='speakername'),
        Constant('genderLabel'),
        transform=lookup_person_attribute
    )
    speaker_gender.search_filter = MultipleChoiceFilter(
        description="Search only in speeches made by speakers of a certain gender",
        option_count=10
    )

    speaker_birthdate = FieldDefinition(
        name = 'speaker_birthdate',
        display_name = 'Speaker birth date',
        description= 'Date at which the speaker was born',
        es_mapping=date_mapping(),
    )
    speaker_birthdate.extractor = Combined(
        Metadata('speaker_metadata'),
        XML(attribute='person_id'),
        XML(attribute='speakername'),
        Constant('birthdate'),
        transform=lookup_person_atttribute_date
    )

    speaker_deathdate = FieldDefinition(
        name = 'speaker_deathdate',
        display_name = 'Speaker death date',
        description= 'Date at which the speaker was born',
        es_mapping=date_mapping(),
    )
    speaker_deathdate.extractor = Combined(
        Metadata('speaker_metadata'),
        XML(attribute='person_id'),
        XML(attribute='speakername'),
        Constant('deathdate'),
        transform=lookup_person_atttribute_date
    )

    speaker_birthplace = FieldDefinition(
        name = 'speaker_birthplace',
        display_name = 'Speaker birthplace',
        description= 'Place where the speaker was born',
        es_mapping=keyword_mapping(),
    )
    speaker_birthplace.extractor = Combined(
        Metadata('speaker_metadata'),
        XML(attribute='person_id'),
        XML(attribute='speakername'),
        Constant('birthPlaceLabel'),
        transform=lookup_person_attribute
    )

    speaker_wikidata = FieldDefinition(
        name = 'speaker_wikidata',
        display_name = 'Speaker Wikidata URI',
        description= 'URI for the Wikidata page for this speaker',
        es_mapping=keyword_mapping(),
    )
    speaker_wikidata.extractor = Combined(
        Metadata('speaker_metadata'),
        XML(attribute='person_id'),
        XML(attribute='speakername'),
        Constant('wikidata_uri'),
        transform=lookup_person_attribute
    )

    ministerial_role = field_defaults.ministerial_role()
    ministerial_role.extractor = Combined(
        Metadata('current_positions'),
        XML(attribute='person_id'),
        XML(attribute='speakername'),
        transform=lookup_current_ministerial_position
    )
    ministerial_role.search_filter.option_count = 45

    parliamentary_role = field_defaults.parliamentary_role()
    parliamentary_role.extractor = Combined(
        Metadata('current_positions'),
        XML(attribute='person_id'),
        XML(attribute='speakername'),
        transform=lookup_current_parliamentary_position
    )

    party = field_defaults.party()
    party.extractor = Combined(
        Metadata('current_positions'),
        XML(attribute='person_id'),
        XML(attribute='speakername'),
        transform=lookup_current_party
    )

    topic = field_defaults.topic()
    topic.extractor = Combined(
        _speech_id_extractor,
        Metadata('topics'),
        transform=select_topic
    )

    subtopic = field_defaults.subtopic()
    subtopic.extractor = Combined(
        _speech_id_extractor,
        Metadata('subtopics'),
        transform=select_topic
    )

    speech_type = field_defaults.speech_type()
    speech_type.extractor = XML(
        attribute='type'
    )

    def __init__(self):
        self.fields = [
            self.country, self.date,
            self.debate_title, self.debate_id,
            self.topic, self.subtopic,
            self.chamber,
            self.speech, self.speech_id, 
            self.speech_type,
            self.speaker, self.speaker_id,
            self.speaker_gender, self.speaker_birthdate,
            self.speaker_deathdate, self.speaker_birthplace,
            self.speaker_wikidata, self.ministerial_role,
            self.parliamentary_role, self.party
        ]
