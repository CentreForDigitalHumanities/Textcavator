'''
Defines faculty-specific variations of the UU course descriptions corpus

Each faculty corpus is a separate corpus with its own index.
'''

from typing import Callable
from ianalyzer_readers.readers.core import Document
from ianalyzer_readers.extract import CSV

from addcorpus.es_mappings import keyword_mapping
from addcorpus.python_corpora.corpus import FieldDefinition
from corpora.uu_course_descriptions.uu_course_descriptions import UUCourseDescriptions, FACULTIES


_faculty_field = FieldDefinition(
    name='faculty',
    display_name='Faculty',
    extractor=CSV('FACULTEIT', transform=FACULTIES.get),
    es_mapping=keyword_mapping(),
)
'''Adjusted version of the faculty field that does not use a search filter or
visualisation'''

def _faculty_filter(faculty: str) -> Callable[[Document], bool]:
    '''Returns a function that can be used to filter documents by the given faculty'''
    return lambda doc: doc['faculty'] == FACULTIES[faculty.upper()]


class _UUCourseDescriptionsFaculty(UUCourseDescriptions):
    '''
    Parent class for faculty-specific corpora
    '''

    faculty_code = None
    '''The abbreviated name of the faculty'''

    description_page = None

    def source2dicts(self, source, **kwargs):
        all_docs = super().source2dicts(source)
        return filter(_faculty_filter(self.faculty_code), all_docs)

    @property
    def es_index(self):
        return super().es_index + '_' + self.faculty_code

    @property
    def image(self):
        return f'uu_{self.faculty_code}.jpg'

    fields = [
        field if field.name != 'faculty' else _faculty_field
        for field in UUCourseDescriptions.fields
    ]


class UUCourseDescriptionsBETA(_UUCourseDescriptionsFaculty):
    title = 'Faculty of Science'
    description = 'Courses taught at the Faculty of Science in 2024-2025'
    languages = ['nl', 'en']
    faculty_code = 'beta'


class UUCourseDescriptionsDGK(_UUCourseDescriptionsFaculty):
    title = 'Faculty of Vetinary Medicine'
    description = 'Courses taught at the Faculty of Vetinary Medicine in 2024-2025'
    languages = ['nl', 'en']
    faculty_code = 'dgk'


class UUCourseDescriptionsGEO(_UUCourseDescriptionsFaculty):
    title = 'Faculty of Geosciences'
    description = 'Courses taught at the Faculty of Geosciences in 2024-2025'
    languages = ['nl', 'en']
    faculty_code = 'geo'


class UUCourseDescriptionsGNK(_UUCourseDescriptionsFaculty):
    title = 'Faculty of Medicine - UMC Utrecht'
    description = 'Courses taught at the Faculty of Medicine and UMC Utrecht in 2024-2025'
    languages = ['nl', 'en']
    faculty_code = 'gnk'


class UUCourseDescriptionsGW(_UUCourseDescriptionsFaculty):
    title = 'Faculty of Humanities'
    description = 'Courses taught at the Faculty of Humanities in 2024-2025'
    faculty_code = 'gw'


class UUCourseDescriptionsREBO(_UUCourseDescriptionsFaculty):
    title = 'Faculty of Law, Economics and Governance'
    description = 'Courses taught at the Faculty of Law, Economics, and Governance in 2024-2025'
    languages = ['nl', 'en']
    faculty_code = 'rebo'


class UUCourseDescriptionsSW(_UUCourseDescriptionsFaculty):
    title = 'Faculty of Social and Behavioural Sciences'
    description = 'Courses taught at the Faculty of Social and Behavioural Sciences in 2024-2025'
    languages = ['nl', 'en']
    faculty_code = 'sw'
