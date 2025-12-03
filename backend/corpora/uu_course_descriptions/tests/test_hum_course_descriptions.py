import os
import pytest

from corpora.utils_test import corpus_from_api
from addcorpus.python_corpora.save_corpus import load_and_save_all_corpora
from addcorpus.python_corpora.load_corpus import load_corpus_definition

here = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture()
def hum_course_descriptions_settings(settings, db):
    settings.CORPORA = {
        'hum_course_descriptions': os.path.join(here, '../uu_course_descriptions_gw_2023.py')
    }
    settings.HUM_COURSE_DESCRIPTIONS_DATA = os.path.join(here, 'data')

def test_hum_course_descriptions_model(hum_course_descriptions_settings, db, admin_client):
    corpus = corpus_from_api(admin_client, 'hum_course_descriptions')
    assert corpus['title'] == 'Humanities Course Descriptions'

description = '''- Stap 1 cursusinvoer door contactpersonen; Van dinsdag 1 december t/m vrijdag 15 januari
- Stap 2 controle cursusinvoer door opleidings- en programma coördinatoren; van maandag 18 januari t/m vrijdag 29 januari
- Stap 3 controle cursusinvoer door onderwijscoördinatoren van maandag 1 februari t/m donderdag 18 februari (en door OWS)
- Consolidatie vrijdag 19 februari 2021.
Wat een leuk proces is dit toch!
:-)'''

target_docs = [{
    'id': '202100017',
    'academic_year': 2023,
    'name': 'Dummy; TEST 3',
    'type': 'CURSUS',
    'department': 'ONB',
    'description': 'Onbekend',
    'faculty': 'GW',
    'contact': 'L. Tax',
    'teacher': 'L. Tax',
    'program_coordinator': 'L. Tax',
    'course_coordinator': None,
    'min_coordinator': None,
    'coordinator': None,
    'goal': '',
    'content': description,
    'level': 'Bachelor 2',
    'language_code': 'nl',
    'language': 'Dutch',
}]


def test_hum_course_descriptions_extraction(hum_course_descriptions_settings):
    load_and_save_all_corpora()
    corpus = load_corpus_definition('hum_course_descriptions')
    assert corpus

    docs = list(corpus.documents())
    assert len(docs) == 1
    assert docs == target_docs
