from datetime import datetime
from glob import glob
import re
from bs4 import BeautifulSoup
from pathlib import Path, PurePath

from django.conf import settings

from ianalyzer_readers.xml_tag import Tag
from ianalyzer_readers.extract import Constant, XML, Metadata, Cache, Combined


from addcorpus.python_corpora.corpus import XMLCorpusDefinition
from addcorpus.python_corpora.filters import MultipleChoiceFilter
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

def select_topic(input):
        full_speech_id, topic_dict = input
        speech_id = abbreviate_speech_id(full_speech_id)
        previous_topic = ''
        for key in topic_dict:
            if float(key) > float(speech_id):
                return previous_topic
            else:
                previous_topic = topic_dict[key]


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
        for directory in [dir for dir in Path(self.data_directory).iterdir() if dir.is_dir()]:
            for xml_file in glob('*.xml', root_dir=directory):
                full_path = self.data_directory / directory / xml_file
                metadata['date'] = extract_date(xml_file)
                metadata['chamber'] = extract_chamber(xml_file)
                metadata['debate_title'] = generate_title(metadata['chamber'], metadata['date'])
                metadata['debate_id'] = extract_debate_id(xml_file)
                metadata['topics'], metadata['subtopics'] = extract_topics_and_subtopics(self.data_directory / directory / xml_file)
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
        ]
