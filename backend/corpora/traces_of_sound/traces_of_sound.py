from glob import glob
from copy import copy
import re
from typing import Dict

from django.conf import settings
from ianalyzer_readers.extract import Backup, CSV

from addcorpus.es_mappings import keyword_mapping
from addcorpus.es_settings import es_settings
from addcorpus.python_corpora.corpus import CSVCorpusDefinition, FieldDefinition
from addcorpus.python_corpora.filters import MultipleChoiceFilter
from corpora.dutchnewspapers.dutchnewspapers_public import DutchNewspapersPublic

class RegexCSV(CSV):
    '''Adjusted CSV extractor that fetches all columns matching a regular expression.'''
    def _apply(self, rows, *nargs, **kwargs):
        return self.get_values(rows[0])

    def get_values(self, row):
        return { key: value for key, value in row.items() if re.search(self.field, key) }


def format_tags(data: Dict):
    if data:
        tags = [key for key, value in data.items() if value == 'True']
        if len(tags):
            return [tag.split(": ")[-1] for tag in tags]

class TracesOfSound(CSVCorpusDefinition):
    '''
    Corpus with references to sound in Dutch newspapers (and ultimately, other sources)
    '''

    title = "Traces of Sound"
    description = "Articles from Dutch newspapers in the public domain with references " \
        "to sound. This is an annotated collection from the 'Dutch Newspapers (public)' " \
        "corpus."
    min_date = DutchNewspapersPublic.min_date
    max_date = DutchNewspapersPublic.max_date
    data_directory = settings.TRACES_OF_SOUND_DATA
    es_index = getattr(settings, 'TRACES_OF_SOUND_ES_INDEX', 'traces-of-sound')
    languages = DutchNewspapersPublic.languages
    category = DutchNewspapersPublic.category
    description_page = 'traces_of_sound.md'
    image = 'Oren.webp'
    word_model_path = getattr(settings, "DUTCHNEWSPAPERS_WM", None)
    delimiter = ';'

    @property
    def es_settings(self):
        return es_settings(self.languages[:1])

    def sources(self, **kwargs):
        for csv_file in glob(f"{self.data_directory}/*.csv"):
            yield csv_file

    sound_affect = FieldDefinition(
        name="sound_affect",
        display_name="Sound affect",
        description="The affect evoked by the sound.",
        es_mapping=keyword_mapping(),
        extractor=RegexCSV('tag: Affect: ', transform=format_tags),
        search_filter=MultipleChoiceFilter(
            description="Accept only articles with these sound affects.",
        ),
    )

    sound_context = FieldDefinition(
        name="sound_context",
        display_name="Sound context",
        description="The context of the sound.",
        es_mapping=keyword_mapping(),
        extractor=RegexCSV('tag: Context: ', transform=format_tags),
        search_filter=MultipleChoiceFilter(
            description="Accept only articles with these sound contexts.",
        ),
    )

    sound_effect = FieldDefinition(
        name="sound_effect",
        display_name="Sound effect",
        description="The effect of the sound.",
        es_mapping=keyword_mapping(),
        extractor=RegexCSV('tag: Effect: ', transform=format_tags),
        search_filter=MultipleChoiceFilter(
            description="Accept only articles in which sound had these effects.",
        ),
    )

    sound_evocation = FieldDefinition(
        name="sound_evocation",
        display_name="Sound evocation",
        description="The association the sound evoked.",
        es_mapping=keyword_mapping(),
        extractor=RegexCSV('tag: Evocation: ', transform=format_tags),
        search_filter=MultipleChoiceFilter(
            description="Accept only articles in which sounds evoked this association.",
        ),
    )

    sound_function = FieldDefinition(
        name="sound_function",
        display_name="Sound function",
        description="The function of the sound.",
        es_mapping=keyword_mapping(),
        extractor=RegexCSV('tag: Function: ', transform=format_tags),
        search_filter=MultipleChoiceFilter(
            description="Accept only articles with these sound functions.",
        ),
    )

    sound_location = FieldDefinition(
        name="sound_location",
        display_name="Sound location",
        description="The location of the sound.",
        es_mapping=keyword_mapping(),
        extractor=Backup(
            RegexCSV('tag: Location: ', transform=format_tags),
            RegexCSV('tag: Geolocation: ', transform=format_tags),
            RegexCSV('tag: LOO: ', transform=format_tags),
            RegexCSV('tag: LOP: ', transform=format_tags),
        ),
        search_filter=MultipleChoiceFilter(
            description="Accept only articles with these sound locations.",
        ),
    )

    sound_source = FieldDefinition(
        name="sound_source",
        display_name="Sound source",
        description="The source of the sound.",
        es_mapping=keyword_mapping(),
        extractor=Backup(
            RegexCSV('tag: Source: ', transform=format_tags),
            RegexCSV('tag: Carrier: ', transform=format_tags),
        ),
        search_filter=MultipleChoiceFilter(
            description="Accept only articles with these sound sources.",
        ),
    )

    sound_time = FieldDefinition(
        name="sound_time",
        display_name="Sound time",
        description="The time of the sound.",
        es_mapping=keyword_mapping(),
        extractor=RegexCSV('tag: Time: ', transform=format_tags),
        search_filter=MultipleChoiceFilter(
            description="Accept only articles in which sounds occurred in this time.",
        ),
    )

    sound_type = FieldDefinition(
        name="sound_type",
        display_name="Sound type",
        description="The type of sound.",
        es_mapping=keyword_mapping(),
        extractor=Backup(
            RegexCSV('tag: Type: ', transform=format_tags),
            RegexCSV('tag: Sound: ', transform=format_tags),
        ),
        search_filter=MultipleChoiceFilter(
            description="Accept only articles with these sound types.",
        ),
    )

    extra_fields = [
        sound_source,
        sound_location,
        sound_type,
        sound_evocation,
        sound_function,
        sound_effect,
        sound_affect,
        sound_time,
    ]

    @property
    def fields(self):
        base_fields = [
            self._copy_field(field) for field in DutchNewspapersPublic().fields
        ]
        return base_fields[:1] + self.extra_fields + base_fields[1:]

    def _copy_field(self, field: FieldDefinition) -> FieldDefinition:
        clone = copy(field)
        clone.extractor = CSV(field.name)
        return clone
