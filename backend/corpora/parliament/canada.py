from datetime import datetime
from glob import glob
import logging
import re

from corpora.parliament.parliament import Parliament
from corpora.utils.constants import document_context
from textcavator_readers.extract import Constant, CSV
from addcorpus.python_corpora.corpus import CSVCorpusDefinition
import corpora.parliament.utils.field_defaults as field_defaults
from corpora.parliament.uk import format_house

class ParliamentCanada(Parliament, CSVCorpusDefinition):
    title = 'People & Parliament (Canada)'
    description = "Speeches from House of Commons"
    min_date = datetime(year=1901, month=1, day=1)
    es_index = 'parliament-canada'

    image = 'canada.jpeg'
    languages = ['en']
    description_page = 'canada.md'
    field_entry = 'speech_id'
    required_field = 'content'

    document_context = document_context(sort_field=None)

    def sources(self, start, end):
        logger = logging.getLogger('indexing')
        for csv_file in glob('{}/*.csv'.format(self.data_directory)):
            yield csv_file, {}

    chamber = field_defaults.chamber()
    chamber.extractor = CSV(
        'house',
        transform=format_house
    )
    # remove search filter and visualisations since there is only value in the data
    chamber.search_filter = None
    chamber.visualizations = None

    country = field_defaults.country()
    country.extractor = Constant(
        value='Canada'
    )

    date = field_defaults.date()
    date.extractor = CSV('date_yyyy-mm-dd')
    date.search_filter.lower = min_date

    debate_id = field_defaults.debate_id()
    debate_id.extractor = CSV(
        'speech_id',
        transform=lambda x: x[:re.search(r'\d{4}-\d{2}-\d{2}', x).span()[1]]
    )

    debate_title = field_defaults.debate_title()
    debate_title.extractor = CSV('heading1')

    party = field_defaults.party()
    party.extractor = CSV('speaker_party')

    role = field_defaults.parliamentary_role()
    role.extractor = CSV('speech_type')

    speaker = field_defaults.speaker()
    speaker.extractor = CSV('speaker_name')

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = CSV('speaker_id')

    speaker_constituency = field_defaults.speaker_constituency()
    speaker_constituency.extractor = CSV('speaker_constituency')

    speech = field_defaults.speech(language='en')
    speech.extractor = CSV(
        'content',
        multiple=True,
        transform=lambda x : ' '.join(x)
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = CSV('speech_id')

    topic = field_defaults.topic()
    topic.extractor = CSV('heading2')

    subtopic = field_defaults.subtopic()
    subtopic.extractor = CSV('heading3')

    def __init__(self):
        self.fields = [
            self.country, self.date,
            self.debate_id, self.debate_title,
            self.chamber,
            self.speaker, self.speaker_id, self.speaker_constituency, self.role, self.party,
            self.speech, self.speech_id,
            self.topic, self.subtopic,
        ]
