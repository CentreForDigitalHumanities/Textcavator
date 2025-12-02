from datetime import date, datetime
import os
import csv
import re
import operator
from typing import Optional, Iterable, Callable, Dict, List, Tuple
from bs4.element import Tag as BS4Tag

from django.conf import settings
from ianalyzer_readers.readers.xml import XMLReader
from ianalyzer_readers.extract import Constant, XML, Combined, Metadata, Order, Pass, Cache
from ianalyzer_readers.xml_tag import Tag, PreviousSiblingTag, TransformTag
from ianalyzer_readers.readers.core import Field
from tqdm import tqdm

from corpora.parliament.parliament import Parliament
from corpora.parliament.utils import field_defaults
from addcorpus.es_mappings import date_estimate_mapping, date_mapping
from addcorpus.python_corpora.filters import DateFilter
from addcorpus.python_corpora.corpus import FieldDefinition
from api.utils import document_link
from corpora.parliament.sweden import ParliamentSweden

def _find(items: Iterable, predicate: Callable):
    return next((item for item in items if predicate(item)), None)


def _group_metadata(csv_filename: str, group_by: str) -> Dict[str, List[Dict[str, str]]]:
    '''
    Collect metadata from CSV file and group by ID
    '''
    data = {}
    with open(csv_filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            group = row.copy().pop(group_by)
            if group in data:
                data[group] += [row]
            else:
                data[group] = [row]
    return data


def _get_speaker_data(speaker_id, all_data) -> List[Dict]:
    '''Convenience function to get metadata associated with a speaker, from a data
    table grouped by speaker ID.'''
    return all_data.get(speaker_id, [])

def _parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, '%Y-%m-%d').date()

def _get_date_range(date_values: List[str]) -> Tuple[date, date]:
    dates = [_parse_date(value) for value in date_values]
    return min(dates), max(dates)

def _format_date(value: date) -> str:
    return value.strftime('%Y-%m-%d')

def _format_date_range(values: Tuple[date, date]) -> Dict:
    return {'gte': _format_date(values[0]), 'lte':  _format_date(values[1])}

def _get_approximate_date(date_range: Tuple[date, date]) -> date:
    start, end = date_range
    return start + (end - start) / 2

def _is_day(date_str: str) -> bool:
    return re.match(r'\d{4}-\d{2}-\d{2}', date_str) is not None

def _is_year(date_str: str) -> bool:
    return date_str.isnumeric()

def _year_from_date_str(value: str) -> Optional[int]:
    if _is_day(value):
        date = _parse_date(value)
        return date.year
    if _is_year(value):
        return int(value)

def _get_speaker_birth_year(values) -> Optional[int]:
    speaker_data = _get_speaker_data(*values)
    if speaker_data:
        speaker_datum = speaker_data[0]
        return _year_from_date_str(speaker_datum['born'])

def _get_speaker_death_year(values) -> Optional[int]:
    speaker_data = _get_speaker_data(*values)
    if speaker_data:
        speaker_datum = speaker_data[0]
        return _year_from_date_str(speaker_datum['dead'])

def _get_speaker_gender(values) -> Optional[str]:
    speaker_data = _get_speaker_data(*values)
    if speaker_data:
        speaker_datum = speaker_data[0]
        return speaker_datum['gender']

def _get_speaker_name(values) -> Optional[str]:
    speaker_data = _get_speaker_data(*values)
    is_primary = lambda d: d['primary_name'] == 'True'
    primary_datum = _find(speaker_data, is_primary)
    if primary_datum:
        return primary_datum['name']

def _compare_dates(date_str: str, limit: date, compare: Callable):
    if _is_day(date_str):
        start = _parse_date(date_str)
        return compare(start, limit)
    if _is_year(date_str):
        start_year = int(date_str)
        return compare(start_year, limit.year)

def _in_date_range(datum: Dict, debate_date_range: Tuple[date, date]) -> bool:
    '''
    Whether the debate date is in range of a data row with a date range.
    Returns `False` if the data row has no date.
    '''

    debate_start, debate_end = debate_date_range
    return _compare_dates(datum['start'], debate_end, operator.le) \
        and _compare_dates(datum['end'], debate_start, operator.ge)

def _filter_in_date_range(data: List, date_range: Tuple[date, date]) -> List:
    is_in_range = lambda d: _in_date_range(d, date_range)
    return list(filter(is_in_range, data))


def _get_party_affiliation(values) -> Dict:
    '''Return party affiliation data for the speaker'''
    speaker_id, date_str, all_affiliation_data = values
    speaker_affiliations = _get_speaker_data(speaker_id, all_affiliation_data)

    # check for a dated affiliation
    if current := _filter_in_date_range(speaker_affiliations, date_str):
        return current[0]

    # if no dated affiliation, return the primary (or None)
    is_primary = lambda d: not (d['start'] or d['end'])
    return _find(speaker_affiliations, is_primary)


def _get_speaker_party(values):
    affiliation = _get_party_affiliation(values)
    if affiliation:
        return affiliation['party']

def _get_speaker_party_id(values):
    affiliation = _get_party_affiliation(values)
    if affiliation:
        return affiliation['party_id']

def _get_speaker_wiki_id(values):
    speaker_data = _get_speaker_data(*values)
    if speaker_data:
        return speaker_data[0]['wiki_id']

def _get_ministerial_role(values):
    speaker_id, date_range, all_data = values
    speaker_roles = _get_speaker_data(speaker_id, all_data)

    if current := _filter_in_date_range(speaker_roles, date_range):
        roles = set(datum['role'] for datum in current)
        return list(roles)

def _get_parliamentary_role(values):
    speaker_id, date_range, all_data = values
    speaker_roles = _get_speaker_data(speaker_id, all_data)

    if current := _filter_in_date_range(speaker_roles, date_range):
        return current[0]['role']

def _get_speaker_constituency(values):
    speaker_id, date_range, all_data = values
    speaker_roles = _get_speaker_data(speaker_id, all_data)

    if current := _filter_in_date_range(speaker_roles, date_range):
        return current[0]['district']

def _is_known(speaker_id: str) -> bool:
    return speaker_id and speaker_id != 'unknown'


def _is_in_sweden_corpus_range(debate_date_range: Tuple[date, date]) -> bool:
    return ParliamentSweden.min_date < debate_date_range[0] < ParliamentSweden.max_date

def _format_sweden_corpus_link(speech_id: str) -> str:
    # For the sake of simplicity, this just assumes that the sweden corpus is called
    # `parliament-sweden`
    return document_link('parliament-sweden', speech_id)


_chambers = {
    'ak': 'Andra Kammaren',
    'fk': 'Första Kammaren',
    'ek': 'Riksdag'
}


def _correct_records_path(path: str) -> str:
    '''
    Fixes incorrect file paths, see https://github.com/swerik-project/riksdagen-records/issues/129
    '''

    return path.replace('/199920/', '/19992000/')


class SwerikMetadataReader(XMLReader):
    '''Extracts XML file index from metadata file. This step is needed to get Chamber
    metadata.'''

    tag_entry = Tag('xi:include')
    data_directory = os.path.join(
        settings.PP_SWEDEN_SWERIK_DATA, 'records', 'data'
    )

    def sources(self, **kwargs):
        for chamber in _chambers.keys():
            path = os.path.join(self.data_directory, f'prot-{chamber}.xml')
            yield path, {'chamber': chamber}

    fields = [
        Field(name='path', extractor=XML(attribute='href', transform=_correct_records_path)),
        Field(name='chamber', extractor=Metadata('chamber')),
    ]

def _iterate_utterance_sequence(element: BS4Tag) -> Iterable[BS4Tag]:
    yield element

    if element.has_attr('next'):
        next_element = element.find_next_sibling(name='u', attrs={'xml:id': element['next']})
        if next_element:
            for el in _iterate_utterance_sequence(next_element):
                yield el


def _extract_utterance_text(element: BS4Tag) -> str:
    raw = element.getText()
    clean = re.sub(r'\s+', ' ', raw).strip()
    return clean


class ParliamentSwedenSwerik(Parliament, XMLReader):
    title = 'People & Parliament (Sweden, Swerik dataset)'
    description = 'Speeches from the Riksdag. This corpus is based on data published ' \
        'by the Swerik project.'
    min_date = date(1867, 1, 1)
    max_date = date(2023, 12, 31)
    languages = ['sv']
    image = 'sweden.jpg'
    description_page = 'sweden-swerik.md'

    data_directory = settings.PP_SWEDEN_SWERIK_DATA
    es_index = getattr(settings, 'PP_SWEDEN_SWERIK_INDEX', 'parliament-sweden-swerik')

    tag_toplevel = Tag('TEI')
    tag_entry = Tag('u', attrs={'prev': None})

    def sources(self, **kwargs):
        print('Extracting person metadata...')
        metadata = self._collect_person_metadata()

        print('Extracting records...')
        records_reader = SwerikMetadataReader()
        records = list(records_reader.documents())

        for doc in tqdm(records):
            path = os.path.join(records_reader.data_directory, doc['path'])
            doc.update(metadata)
            yield path, doc

    def _collect_person_metadata(self):
        persons_path = os.path.join(self.data_directory, 'persons', 'data')

        metadata = dict()
        datafiles = ['person', 'party_affiliation', 'name', 'wiki_id', 'minister',
            'member_of_parliament'
        ]

        for datafile in datafiles:
            path = os.path.join(persons_path, datafile + '.csv')
            data = _group_metadata(path, 'person_id')
            metadata[datafile] = data

        return metadata


    _speaker_id_extractor = Cache(XML(attribute='who'))
    _date_extractor = Cache(
        XML(
            Tag('text', recursive=False),
            Tag('front', recursive=False),
            Tag('docDate'),
            toplevel=True,
            attribute='when',
            multiple=True,
            transform=_get_date_range,
        ),
        level='source',
    )

    chamber = field_defaults.chamber(count=3)
    chamber.extractor = Metadata('chamber', transform=_chambers.get)

    country = field_defaults.country()
    country.extractor = Constant('Sweden')

    date = field_defaults.date(min_date, max_date)
    date.description = 'Date on which the debate took place (may be approximate)'
    date.extractor = Pass(
        Pass(_date_extractor, transform=_get_approximate_date),
        transform=_format_date,
    )

    date_range = FieldDefinition(
        name='date_range',
        display_name='Date range',
        description='Date range for the debate',
        es_mapping=date_estimate_mapping(),
        extractor=Pass(
            _date_extractor,
            transform=_format_date_range,
        )
    )

    debate_id = field_defaults.debate_id()
    debate_id.extractor = XML(
        toplevel=True,
        attribute='xml:id',
    )

    ministerial_role = field_defaults.ministerial_role()
    ministerial_role.extractor = Combined(
        _speaker_id_extractor,
        _date_extractor,
        Metadata('minister'),
        transform=_get_ministerial_role,
    )

    parliamentary_role = field_defaults.parliamentary_role()
    parliamentary_role.extractor = Combined(
        _speaker_id_extractor,
        _date_extractor,
        Metadata('member_of_parliament'),
        transform=_get_parliamentary_role,
    )

    party = field_defaults.party()
    party.extractor = Combined(
        _speaker_id_extractor,
        _date_extractor,
        Metadata('party_affiliation'),
        transform=_get_speaker_party,
    )

    party_id = field_defaults.party_id()
    party_id.extractor = Combined(
        _speaker_id_extractor,
        _date_extractor,
        Metadata('party_affiliation'),
        transform=_get_speaker_party_id,
    )

    sequence = field_defaults.sequence()
    sequence.extractor = Order(transform = lambda n: n + 1)

    speaker = field_defaults.speaker()
    speaker.extractor = Combined(
        _speaker_id_extractor,
        Metadata('name'),
        transform=_get_speaker_name,
    )

    speaker_constituency = field_defaults.speaker_constituency()
    speaker_constituency.extractor = Combined(
        _speaker_id_extractor,
        _date_extractor,
        Metadata('member_of_parliament'),
        transform=_get_speaker_constituency,
    )

    speaker_birth_year = field_defaults.speaker_birth_year()
    speaker_birth_year.extractor = Combined(
        _speaker_id_extractor,
        Metadata('person'),
        transform=_get_speaker_birth_year,
    )

    speaker_death_year = field_defaults.speaker_death_year()
    speaker_death_year.extractor = Combined(
        _speaker_id_extractor,
        Metadata('person'),
        transform=_get_speaker_death_year,
    )

    speaker_gender = field_defaults.speaker_gender()
    speaker_gender.extractor = Combined(
        _speaker_id_extractor,
        Metadata('person'),
        transform=_get_speaker_gender,
    )

    speaker_id = field_defaults.speaker_id()
    # use the wikidata ID rather than the swerik ID
    speaker_id.extractor = Combined(
        _speaker_id_extractor,
        Metadata('wiki_id'),
        transform=_get_speaker_wiki_id,
    )

    speech = field_defaults.speech(language='sv')
    speech.extractor = XML(
        TransformTag(_iterate_utterance_sequence),
        Tag('seg', recursive=False),
        multiple=True,
        extract_soup_func=_extract_utterance_text,
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = XML(attribute='xml:id')

    topic = field_defaults.topic()
    topic.extractor = XML(
        PreviousSiblingTag('note', type='title'),
        transform=lambda value: str.strip(value) if value else None,
    )

    url_sweden_corpus = FieldDefinition(
        name='url_sweden_corpus',
        display_name='Speech in Sweden 1920-2022 corpus',
        description='Link to the corresponding speech in the Sweden 1920-2022 corpus',
        display_type='url',
        hidden=getattr(settings, 'PP_SWEDEN_SWERIK_HIDE_CROSSCORPUS_LINK', False),
        es_mapping = {'type': 'keyword', 'index': False, 'doc_values': False},
        extractor=XML(
            attribute='xml:id',
            applicable=Combined(
                Pass(_date_extractor, transform=_is_in_sweden_corpus_range),
                # speeches with unknown speaker are apparently not included in the sweden corpus
                Pass(_speaker_id_extractor, transform=_is_known),
                transform=all,
            ),
            transform=_format_sweden_corpus_link,
        )
    )

    def __init__(self):
        self.fields = [
            self.chamber,
            self.country,
            self.date,
            self.date_range,
            self.debate_id,
            self.ministerial_role,
            self.parliamentary_role,
            self.party,
            self.party_id,
            self.speaker,
            self.speaker_constituency,
            self.speaker_gender,
            self.speaker_birth_year,
            self.speaker_death_year,
            self.speaker_id,
            self.sequence,
            self.speech,
            self.speech_id,
            self.topic,
            self.url_sweden_corpus,
        ]
