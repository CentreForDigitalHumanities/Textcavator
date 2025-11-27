import pytest
from django.contrib.auth.models import Group

from addcorpus.models import Corpus
from es.views import NamedEntitySearchView
from es.client import elasticsearch

@pytest.fixture()
def annotated_corpus_public(annotated_mock_corpus):
    basic_group = Group.objects.create(name='basic')
    corpus = Corpus.objects.get(name=annotated_mock_corpus)
    corpus.groups.add(basic_group)


def test_ner_search_view(
    client, annotated_mock_corpus, index_annotated_mock_corpus, annotated_corpus_public,
):
    route = f'/api/es/{annotated_mock_corpus}/0/named_entities'
    response = client.get(route, content_type='application/json')
    assert response.status_code == 200


def test_construct_ner_query():
    viewset = NamedEntitySearchView()
    query = viewset.construct_named_entity_query('my_identifier')
    expected = {
        "bool": {
            "must": {"term": {"id": "my_identifier"}},
            "should": [
                {"exists": {"field": "location:ner-kw"}},
                {"exists": {"field": "miscellaneous:ner-kw"}},
                {"exists": {"field": "organization:ner-kw"}},
                {"exists": {"field": "person:ner-kw"}},
            ],
        }
    }
    assert query == expected


def test_find_named_entity_fields(annotated_mock_corpus, index_annotated_mock_corpus):
    viewset = NamedEntitySearchView()
    client = elasticsearch(annotated_mock_corpus)
    corpus = Corpus.objects.get(name=annotated_mock_corpus)

    fields = viewset.find_named_entity_fields(
        client, corpus.configuration.es_index
    )
    assert len(fields) == 1
    assert fields[0] == 'content:ner'


def test_find_entities():
    viewset = NamedEntitySearchView()
    text = '[Guybrush Threepwood](PER) is looking for treasure on [Monkey Island](LOC)'
    output = viewset.find_entities(text)
    expected = [{'entity': 'person', 'text': 'Guybrush Threepwood'},
                {'entity': 'flat', 'text': ' is looking for treasure on '},
                {'entity': 'location', 'text': 'Monkey Island'}]
    assert output == expected
