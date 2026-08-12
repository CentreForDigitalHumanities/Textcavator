from glob import glob
import logging
from datetime import datetime
import os
import json
import csv
import re

from ianalyzer_readers.extract import Combined, Constant, CSV, Metadata, Pass
from addcorpus.python_corpora.corpus import CSVCorpusDefinition
from addcorpus.python_corpora.filters import MultipleChoiceFilter, DateFilter
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
from corpora.utils.constants import document_context

def format_debate_title(title):
    if title.endswith('.'):
        title = title[:-1]

    return title.title()

def format_house(house):
    if 'commons_wmhall' in house.lower():
        return 'House of Commons - Westminster Hall'
    elif 'commons' in house.lower():
        return 'House of Commons'
    elif 'lords' in house.lower():
        return 'House of Lords'

def format_speaker(speaker):
    if speaker:
        if speaker.startswith('*'):
            speaker = speaker[1:]

        return speaker.title()

def lookup_variable(metadata_tuple):
    name, lookup_dict, variable = metadata_tuple
    if name in lookup_dict and variable in lookup_dict[name]:
        return lookup_dict[name][variable]
    
def transform_date_to_year(date):
    if date:
        return date[0:4]
    else:
        return None

def find_current_positions(positions, date):
    current_position_list = []
    for position in positions:
        if 'startTime' in position and 'endTime' in position:
            start_time = datetime.strptime(position['startTime'][:10], "%Y-%m-%d")
            end_time = datetime.strptime(position['endTime'][:10], "%Y-%m-%d")
            if start_time < datetime.strptime(date, "%Y-%m-%d") < end_time:
                current_position_list.append(position)
        elif 'startTime' in position and start_time < datetime.strptime(date, "%Y-%m-%d"):
            current_position_list.append(position)
    return current_position_list



def lookup_current_ministerial_position(lookup_tuple):
    name, metadata, date = lookup_tuple
    if metadata[name]:
        current_positions = find_current_positions(metadata[name]['positions'], date)
        for position in current_positions:
            if position['minister']:
                return position['positionLabel']

class ParliamentUK(Parliament, CSVCorpusDefinition):
    title = 'People & Parliament (UK)'
    description = "Speeches from the House of Lords and House of Commons"
    min_date = datetime(year=1803, month=1, day=1)
    max_date = datetime(year=2021, month=12, day=31)
    es_index = 'parliament-uk'

    image = 'uk.jpeg'
    languages = ['en']
    description_page = 'uk.md'
    field_entry = 'speech_id'
    document_context = document_context()

    def sources(self, start, end):
        logger = logging.getLogger('indexing')
        with open(os.path.join(self.data_directory, 'merged_metadata_twfy_keys.json'), 'r', encoding='utf-8') as file:
             all_person_metadata = json.load(file)
            
        for csv_file in glob('{}/*.csv'.format(self.data_directory)):
            year = re.search(r'\d{4}', csv_file)[0]

            with open(os.path.join(self.data_directory, 'metadata_conversion_per_year/conversion_dict_{}.json'.format(year))) as file:
                conversion_dict = json.load(file)

            metadata = {}
            metadata_this_year = {}
            for speaker_name in conversion_dict:
                metadata_this_year[speaker_name] = all_person_metadata[conversion_dict[speaker_name]]
            metadata['metadata_this_year'] = metadata_this_year

            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',', quotechar='"')
                speaker_ids = []
                for line in reader:
                    if line and len(line) > 3 and line[3] not in speaker_ids:
                        speaker_ids.append(line[3].split('/')[-1])
            yield csv_file, metadata

    chamber =  field_defaults.chamber()
    chamber.extractor = CSV(
        'house',
        transform=format_house
    )
    chamber.search_filter.option_count = 3

    country = field_defaults.country()
    country.extractor = Constant(
        value='United Kingdom'
    )

    date = field_defaults.date()
    date.extractor = CSV('date')

    debate_title = field_defaults.debate_title()
    debate_title.extractor = CSV(
        'debate',
        transform=format_debate_title
    )
    debate_title.language = 'en'

    debate_id = field_defaults.debate_id()
    debate_id.extractor = CSV('debate_id')

    speech = field_defaults.speech(language='en')
    speech.extractor = CSV(
        'content',
        multiple=True,
        transform=lambda x : ' '.join(x)
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = CSV('speech_id')

    speech_type = field_defaults.speech_type()
    speech_type.extractor = CSV('speech_type')

    speaker = field_defaults.speaker()
    speaker.extractor = CSV(
        'speaker_name',
        transform=format_speaker
    )

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = CSV('speaker_id')

    speaker_gender = field_defaults.speaker_gender()
    speaker_gender.extractor = Combined(
        CSV('speaker_name'),
        Metadata('metadata_this_year'),
        Constant('genderLabel'),
        transform=lookup_variable
    )
    speaker_gender.search_filter = MultipleChoiceFilter(
        description="Search only in speeches from speakers with a specific gender"
    )

    speaker_birth_year = field_defaults.speaker_birth_year()
    speaker_birth_year.extractor = Pass(
        Combined(
            CSV('speaker_name'),
            Metadata('metadata_this_year'),
            Constant('birthdate'),
            transform=lookup_variable
        ),
        transform=transform_date_to_year
    )
    speaker_birth_year.visualizations = ['resultscount', 'termfrequency']
    
    speaker_death_year = field_defaults.speaker_death_year()
    speaker_death_year.extractor = Pass(
        Combined(
            CSV('speaker_name'),
            Metadata('metadata_this_year'),
            Constant('deathdate'),
            transform=lookup_variable
        ),
        transform=transform_date_to_year
    )
    speaker_death_year.visualizations = ['resultscount', 'termfrequency']
    
    speaker_birthplace = field_defaults.speaker_birthplace()
    speaker_birthplace.extractor = Combined(
        CSV('speaker_name'),
        Metadata('metadata_this_year'),
        Constant('birthPlaceLabel'),
        transform=lookup_variable
    )

    speaker_wikidata = field_defaults.speaker_wikidata()
    speaker_wikidata.extractor = Combined(
        CSV('speaker_name'),
        Metadata('metadata_this_year'),
        Constant('wikidata_uri'),
        transform=lookup_variable
    )

    ministerial_role = field_defaults.ministerial_role()
    ministerial_role.extractor = Combined(
        CSV('speaker_name'),
        Metadata('metadata_this_year'),
        CSV('date'),
        transform=lookup_current_ministerial_position
    )

    

    topic = field_defaults.topic()
    topic.extractor = CSV('heading_major',)
    topic.language = 'en'

    subtopic = field_defaults.subtopic()
    subtopic.extractor = CSV('heading_minor')
    subtopic.language = 'en'

    sequence = field_defaults.sequence()
    sequence.extractor = CSV('sequence')

    def __init__(self):
        self.fields = [
            self.country, self.date,
            self.debate_title, self.debate_id,
            self.topic, self.subtopic,
            self.chamber,
            self.speech, self.speech_id, self.speech_type,
            self.sequence,
            self.speaker, self.speaker_id,
            self.speaker_gender, self.speaker_birth_year,
            self.speaker_death_year, self.speaker_birthplace,
            self.speaker_wikidata, self.ministerial_role,
            #self.parliamentary_role, self.party,
        ]
