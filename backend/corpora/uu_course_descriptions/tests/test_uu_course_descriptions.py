import os
import pytest

from corpora.utils_test import corpus_from_api
from addcorpus.python_corpora.save_corpus import load_and_save_all_corpora
from addcorpus.python_corpora.load_corpus import load_corpus_definition

here = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture()
def uu_course_descriptions_settings(settings, db):
    settings.CORPORA = {
        'uu_course_descriptions': 'corpora.uu_course_descriptions.uu_course_descriptions.UUCourseDescriptions'
    }
    settings.UU_COURSE_DESCRIPTIONS_DATA = os.path.join(here, 'data')

def test_uu_course_descriptions_model(uu_course_descriptions_settings, db, admin_client):
    corpus = corpus_from_api(admin_client, 'uu_course_descriptions')
    assert corpus['title'] == 'All faculties'

goal = '''- Begrijpen van de functie van testen in software.
- Het kunnen schrijven van unittest functies op basis van een specificatie
- Het kunnen toepassen van een test-driven workflow bij het oplossen van bugs'''
description = '''In deze cursus leren studenten de basis van testen in softwareontwikkeling.
In de hoorcolleges wordt ingegaan op de motivatie om te testen, en leren studenten over de integratie van testen in een development-workflow.
In practica leren studenten om zelf tests te schrijven aan de hand van praktische opdrachten.'''

target_docs = [
    {
        'id': 100000001,
        'academic_year': 2024,
        'name': 'Inleiding software testen',
        'type': 'CURSUS',
        'department': 'CDH',
        'department_description': 'Digitale Geesteswetenschappen',
        'faculty': 'Geesteswetenschappen',
        'term': 1,
        'exam_goal': 'Bachelor',
        'level': 'Bachelor 1',
        'contact': ['A. de Tester'],
        'teacher': ['B. Test'],
        'examinator': None,
        'course_coordinator': None,
        'goal': goal,
        'content': description,
        'language_code': 'nl',
        'language': 'Dutch',
    }, {
        'id': 100000002,
        'academic_year': 2024,
        'name': 'Test-driven development',
        'type': 'CURSUS',
        'department': 'CDH',
        'department_description': 'Digitale Geesteswetenschappen',
        'faculty': 'Geesteswetenschappen',
        'term': 2,
        'level': 'Bachelor 2',
        'exam_goal': 'Bachelor',
        'contact': ['C. van Testen'],
        'teacher': ['D. Testing', 'E. Tester'],
        'examinator': None,
        'course_coordinator': None,
        'goal': '',
        'content': '',
        'language_code': None,
        'language': 'Unknown',
    }
]


def test_uu_course_descriptions_extraction(uu_course_descriptions_settings):
    load_and_save_all_corpora()
    corpus = load_corpus_definition('uu_course_descriptions')
    assert corpus

    docs = list(corpus.documents())
    assert len(docs) == 3
    for expected, target in zip(docs, target_docs):
        assert expected == target
