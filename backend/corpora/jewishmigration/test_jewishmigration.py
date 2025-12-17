import os
from time import sleep
from unittest.mock import Mock

from elasticsearch import BadRequestError
import pytest
import requests

from addcorpus.es_mappings import geo_mapping
from addcorpus.models import Corpus
from addcorpus.python_corpora.load_corpus import load_corpus_definition
from addcorpus.python_corpora.save_corpus import load_and_save_all_corpora
from indexing.create_job import create_indexing_job
from indexing.run_job import perform_indexing


here = os.path.abspath(os.path.dirname(__file__))


mock_content = [
    {
        "source": "Le Bohec 1981 n. 71",
        "languages": ["Latin", "Greek"],
        "scripts": ["Latin"],
        "place_name": "Constanine/ Cirta",
        "area": "Algeria",
        "region": "Africa Proconsularis ",
        "coordinates": {
            "type": "Point",
            "coordinates": [36.36811466666666, 6.613302666666667],
        },
        "site_type": "Inscription",
        "inscription_type": "Epitaph",
        "period": "II AD",
        "estimated_centuries": ["2", "3"],
        "inscriptions_count": 1,
        "religious_profession": "",
        "sex_dedicator": "",
        "sex_deceased": "Female",
        "symbol": "",
        "comments": "",
        "inscription": "",
        "transcription": "To the shadows of the underworld Julia Victoria the Jewess(?) CV",
    },
    {
        "source": "Le Bohec 1981 n. 72",
        "language": ["Latin"],
        "script": ["Latin"],
        "place_name": "Ksour el-Gannaïa/ Festis",
        "area": "Algeria",
        "region": "Africa Proconsularis ",
        "coordinates": None,
        "site_type": "Inscription",
        "inscription_type": "",
        "period": "VI AD",
        "estimated_centuries": ["4"],
        "inscriptions_count": 1,
        "religious_profession": "",
        "sex_dedicator": "",
        "sex_deceased": "",
        "symbol": "",
        "comments": "Fragment of a marble cancel",
        "inscription": "",
        "transcription": "Fear the faithful (?)",
    },
    {
        "source": "Le Bohec 1981 n. 73",
        "languages": ["Latin"],
        "scripts": ["Latin"],
        "place_name": "Setif",
        "area": "Algeria",
        "region": "Mauretania Caesariensis",
        "coordinates": {"type": "Point", "coordinates": [5.4, 36.18333333333333]},
        "site_type": "Inscription",
        "inscription_type": "Epitaph",
        "period": "VI AD",
        "estimated_centuries": ["3", "4"],
        "inscriptions_count": 1,
        "religious_profession": "",
        "sex_dedicator": "Male",
        "sex_deceased": "Female",
        "symbol": "",
        "comments": "Stone in the form of a box: inscription in a molded frame",
        "inscription": "",
        "transcription": "Caelia Thalassa the Jewess lived for 20 years and 4 months; Marcus Auillius Iaunuaris the loving husband",
    },
]


def mock_response(url: str) -> requests.Response:
    mock = Mock(spec=requests.Response)
    mock.status_code = 200
    mock.json.return_value = mock_content
    return mock


EXPECTED_DOCUMENT = {
    "id": "Le Bohec 1981 n. 71",
    "source_database": "Le Bohec 1981 n. 71",
    "language": ["Latin", "Greek"],
    "script": ["Latin"],
    "language_code": ['la', 'el'],
    "settlement": "Constanine/ Cirta",
    "country": "Algeria",
    "region": "Africa Proconsularis ",
    "coordinates": {
        "type": "Point",
        "coordinates": [36.36811466666666, 6.613302666666667],
    },
    "site_type": "Inscription",
    "inscription_type": "Epitaph",
    "period": "II AD",
    "estimated_centuries": ['2', '3'],
    "inscription_count": 1,
    "religious_profession": "",
    "sex_dedicator": "",
    "sex": "Female",
    "iconography": "",
    "comments": "",
    "transcription": "",
    "transcription_en": "To the shadows of the underworld Julia Victoria the Jewess(?) CV",
}

@pytest.fixture
def jm_corpus_settings(settings):
    settings.CORPORA = {
        'jewishmigration': 'corpora.jewishmigration.jewishmigration.JewishMigration',
    }
    settings.JMIG_DATA_DIR = None
    settings.JMIG_DATA = None
    settings.JMIG_DATA_URL = 'http://www.example.com'
    settings.JMIG_DATA_API_KEY = None
    settings.JMIG_INDEX = 'test-jewishmigration'


@pytest.fixture
def jm_corpus(jm_corpus_settings, db):
    load_and_save_all_corpora()
    corpus = Corpus.objects.get(name='jewishmigration')
    return corpus


@pytest.fixture
def jm_client(es_client, jm_corpus):
    """
    Create and populate an index for a mock corpus in elasticsearch.
    Returns an elastic search client for the mock corpus.
    """
    # add data from mock corpus
    job = create_indexing_job(jm_corpus, mappings_only=True, clear=True)
    perform_indexing(job)

    yield es_client
    # delete index when done
    es_client.indices.delete(index=jm_corpus.configuration.es_index)


def test_jm_validation(db, jm_corpus):
    assert jm_corpus
    assert jm_corpus.configuration_obj
    assert jm_corpus.active


def test_geofield(jm_client, jm_corpus):
    es_index = jm_corpus.configuration.es_index
    assert jm_client.indices.get(index=es_index)
    field_mapping = jm_client.indices.get_field_mapping(
        fields='coordinates', index=es_index)
    assert field_mapping[es_index]['mappings']['coordinates']['mapping']['coordinates'] == geo_mapping()
    geo_data = 'gibberish'
    try:
        jm_client.create(index=es_index, id=1,
                         document={'coordinates': geo_data})
    except Exception as e:
        assert type(e) == BadRequestError
    geo_data = {
        "type": "Point",
            "coordinates": [
                42.0, #longitude east/west
                3.0 #latitude north/south
            ]
    }
    jm_client.create(index=es_index, id=1,
                     document={'coordinates': geo_data})
    document = jm_client.get(index=es_index, id=1)
    assert document['_source']['coordinates'] == geo_data
    query = {
        "geo_bounding_box": {
          "coordinates": {
            "top_left": {
                "lon": 41.0,
                "lat": 5.0
            },
            "bottom_right": {
                "lon": 43.0,
                "lat": 0.0
            }
          }
        }
    }
    # wait for the indexing operation on jm_client to be finished
    sleep(1)
    results = jm_client.search(index=es_index, query=query)
    assert results['hits']['total']['value'] == 1


def test_data_from_request(jm_corpus, monkeypatch):
    monkeypatch.setattr(requests, "get", mock_response)
    corpus_def = load_corpus_definition(jm_corpus.name)
    sources = corpus_def.sources(
        start=corpus_def.min_date, end=corpus_def.max_date)
    documents = list(corpus_def.documents(sources))
    assert len(documents) == 3
    reference_document = documents[0]
    for key in EXPECTED_DOCUMENT.keys():
        assert key in reference_document.keys()
        assert EXPECTED_DOCUMENT[key] == reference_document[key]
