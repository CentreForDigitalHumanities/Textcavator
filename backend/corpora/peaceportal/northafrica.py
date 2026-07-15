import datetime
import os
import re
from typing import List, Optional, Tuple, Union

from addcorpus.es_mappings import main_content_mapping, text_mapping
from addcorpus.python_corpora.corpus import (FieldDefinition,
                                             XLSXCorpusDefinition)
from textcavator_readers.extract import CSV, Constant
from corpora.peaceportal.peaceportal import PeacePortal, transform_to_date_range
from corpora.utils.exclude_fields import exclude_fields_without_extractor
from django.conf import settings


def convert_sex(value: str) -> List[str]:
    convert_table = {
        '?': 'Unknown',
        'X': 'Unknown',
        'M': 'M',
        'F': 'F',
        'M?': 'Unknown'
    }
    sexes = value.strip().split(';')
    return [convert_table[v.strip()] for v in sexes]


def convert_names(value) -> List[str]:
    if not value:
        return []
    return [name.strip() for name in value.split(';')]


def convert_ages(value: Union[str, int]) -> List[int]:
    if isinstance(value, int):
        return value
    split_ages = value.strip().split(';')
    result = []
    for age_string in split_ages:
        try:
            result.append(int(age_string.strip()))
        except ValueError:
            pass
    return result


def convert_languages(value: str) -> List[str]:
    expected_languages = ['greek', 'latin', 'hebrew', 'semitic']
    languages = [lang.strip().replace('(', '').replace(')', '')
                 for lang in value.strip().split(';')]
    return [lang if lang.lower() in expected_languages else 'Unknown' for lang in languages]


def convert_language_codes(value: str) -> List[str]:
    codes = {
        'Greek': 'el',
        'Latin': 'la',
        'Hebrew': 'he',
        'Semitic': 'sem'
    }
    return [codes.get(lang, 'Unknown') for lang in convert_languages(value)]


def convert_dating(value: str) -> Optional[Tuple[int, int]]:
    '''Extract a date range if possible, otherwise use global minimum and maximum'''
    dating_pattern = r'(\d+)\-(\d+)'
    match = re.match(dating_pattern, value)
    if match:
        date_range = transform_to_date_range(datetime.date(year=int(match.group(1)), month=1, day=1),
                                             datetime.date(year=int(match.group(2)), month=12, day=31))
        return date_range
    return transform_to_date_range(None, None)  # Use defaults


def format_comments(values: Tuple):
    '''Format the comment field. Includes:
    - Remarks about age
    '''
    return f'Remarks about age:\t{values[0]}\n'


def convert_none(value: str) -> str:
    if value == 'None':
        return None
    return value


class PeaceportalNorthAfrica(PeacePortal, XLSXCorpusDefinition):
    data_directory = settings.PEACEPORTAL_NORTHAFRICA_DATA
    es_index = getattr(
        settings, 'PEACEPORTAL_NORTHAFRICA_ES_INDEX', 'peaceportal-northafrica')
    title = 'Jewish Epitaphs from North Africa-Carthage'

    def __init__(self):
        super().__init__()
        self.source_database.extractor = Constant(
            value='Jewish Epitaphs from North Africa-Carthage'
        )

        self._id.extractor = CSV(
            'ID', transform=lambda id: f'NorthAfrica_{id}')
        self.transcription.extractor = CSV('Inscription')

        # Combine not before and not after information into date range
        self.date.extractor = CSV('Dating', transform=convert_dating)

        self.names.extractor = CSV('Names ', transform=convert_names)
        self.sex.extractor = CSV('Sex', transform=convert_sex)
        self.age.extractor = CSV('Age', transform=convert_ages)

        remarks_about_age = FieldDefinition(
            name='age_remarks',
            display_name='Remarks about age',
            description='Remarks about the age of the buried person(s)',
            es_mapping=text_mapping(),
            extractor=CSV('Remarks about Age', transform=convert_none),
        )
        self.fields.append(remarks_about_age)
        self.country.extractor = CSV('Country')
        self.settlement.extractor = CSV('Settlement')
        self.location_details.extractor = CSV('Location Details')
        self.language.extractor = CSV(
            'Language', transform=convert_languages)
        self.language_code.extractor = CSV(
            'Language', transform=convert_language_codes)
        self.language_code.hidden = True
        self.iconography.extractor = CSV('Iconography', transform=convert_none)
        self.material.extractor = CSV('Material')
        self.bibliography.extractor = CSV('Bibliography')

        # The transcription is the secondary content field
        self.transcription_english = FieldDefinition(
            name='transcription_en',
            display_name='Translation',
            description='English translation of this inscription.',
            es_mapping=main_content_mapping(
                stopword_analysis=True, stemming_analysis=True, language='en'),
            language='en',
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            extractor=CSV('Translation'),
        )

        # The commentary is the tertiary content field
        self.comments = FieldDefinition(
            name='comments',
            display_name='Commentary',
            description='Extra comments, questions or remarks on this inscription.',
            es_mapping=main_content_mapping(
                stopword_analysis=True, stemming_analysis=True, language='en'),
            language='en',
            search_field_core=True,
            display_type='text_content',
            extractor=CSV('Commentary', transform=convert_none)
        )

        # Remove fields without an extractor, aka fields in parent corpus that are missing
        self.fields = exclude_fields_without_extractor(self.fields)

        # Ensure the correct order of content fields
        # Translation and commentary should be behind transcription, in correct order
        self.fields = list(filter(lambda x: x.name not in [
            'transcription_en', 'comments'], self.fields))
        self.fields += [self.transcription_english, self.comments]

    def sources(self, *args, **kwargs):
        path = os.path.join(self.data_directory,
                            'Jewish Epitaphs from North Africa-Carthage.xlsx')
        yield path
