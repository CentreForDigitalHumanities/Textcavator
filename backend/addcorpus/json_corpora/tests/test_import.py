from addcorpus.json_corpora.import_json import _parse_field
from addcorpus.models import Field, Corpus
from addcorpus.serializers import CorpusJSONDefinitionSerializer
from addcorpus.models import Corpus, CorpusConfiguration, CorpusDocumentationPage
from addcorpus.json_corpora.export_json import export_json_corpus

def test_json_corpus_import(db, json_mock_corpus, json_corpus_definition):
    json_mock_corpus.delete()

    data = {
        'definition': json_corpus_definition,
        'active': True,
    }

    serializer = CorpusJSONDefinitionSerializer(data=data)
    assert serializer.is_valid()
    corpus = serializer.create(serializer.validated_data)

    assert corpus.name == 'example'

    config = corpus.configuration

    assert config.title == 'Example'
    assert config.description == 'Example corpus'
    assert config.languages == ['en']
    assert config.category == 'book'
    assert config.min_year == 1500
    assert config.max_year == 1700
    assert config.source_data_delimiter == ','

    assert len(config.fields.all()) == 2

    character_field = config.fields.get(name='character')
    assert character_field.display_name == 'Character'
    assert character_field.display_type == 'keyword'

    line_field = config.fields.get(name='line')
    assert line_field.display_name == 'Line'
    assert line_field.display_type == 'text_content'


def test_serializer_representation(db, json_mock_corpus, json_corpus_definition):
    json_mock_corpus.delete()

    data = {
        'definition': json_corpus_definition,
        'active': True,
    }

    serializer = CorpusJSONDefinitionSerializer(data=data)
    assert serializer.is_valid()
    corpus = serializer.create(serializer.validated_data)

    serialized = serializer.to_representation(corpus)
    assert json_corpus_definition == serialized['definition']

def test_serializer_update(db, json_corpus_definition, json_mock_corpus: Corpus):
    # edit description
    data = {
        'definition': json_corpus_definition,
        'active': True,
    }
    data['definition']['meta']['description'] = 'A different description'
    serializer = CorpusJSONDefinitionSerializer(data=data)
    assert serializer.is_valid()
    serializer.update(json_mock_corpus, serializer.validated_data)
    corpus_config = CorpusConfiguration.objects.get(corpus=json_mock_corpus)
    assert corpus_config.description == 'A different description'

    # remove a field
    assert Field.objects.filter(corpus_configuration__corpus=json_mock_corpus).count() == 2
    data['definition']['fields'] = data['definition']['fields'][:-1]
    serializer = CorpusJSONDefinitionSerializer(data=data)
    assert serializer.is_valid()
    serializer.update(json_mock_corpus, serializer.validated_data)
    assert Field.objects.filter(corpus_configuration__corpus=json_mock_corpus).count() == 1

def test_serializer_update_field_order(db, json_corpus_definition, json_mock_corpus: Corpus):
    # send corpus with reverse field order
    data = {
        'definition': json_corpus_definition,
        'active': True,
    }
    data['definition']['fields'] = list(reversed(data['definition']['fields']))
    serializer = CorpusJSONDefinitionSerializer(data=data)
    assert serializer.is_valid()
    serializer.update(json_mock_corpus, serializer.validated_data)

    json_mock_corpus.refresh_from_db()
    assert export_json_corpus(json_mock_corpus) == data['definition']


def test_parse_content_field(content_field_json):
    data = _parse_field(content_field_json)
    field = Field(**data)
    assert field.name == 'content'
    assert field.display_name == 'Content'
    assert field.display_type == 'text_content'
    assert field.description == 'Bla bla bla'
    assert field.search_filter == {}
    assert field.results_overview == True
    assert field.csv_core == True
    assert field.search_field_core == True
    assert field.visualizations == ['wordcloud']
    assert field.es_mapping['type'] == 'text'
    assert field.es_mapping['fields'].keys() == {'length', 'clean', 'stemmed'}
    assert field.hidden == False
    assert field.sortable == False
    assert field.searchable == True
    assert field.downloadable == True
    assert field.language == 'en'
    assert field.extract_column == 'content'


def test_parse_keyword_field(keyword_field_json):
    data = _parse_field(keyword_field_json)
    field = Field(**data)
    assert field.name == 'author'
    assert field.display_type == 'keyword'
    assert field.search_filter['name'] == 'MultipleChoiceFilter'
    assert field.search_field_core == False
    assert field.visualizations == ['resultscount', 'termfrequency']
    assert field.es_mapping['type'] == 'keyword'
    assert field.es_mapping['fields'].keys() == {'text'}
    assert field.hidden == False
    assert field.sortable == False
    assert field.searchable == True
    assert field.language == ''


def test_parse_int_field(int_field_json):
    data =  _parse_field(int_field_json)
    field = Field(**data)
    assert field.name == 'year'
    assert field.display_type == 'integer'
    assert field.search_filter['name'] == 'RangeFilter'
    assert field.results_overview == False
    assert field.csv_core == False
    assert field.search_field_core == False
    assert field.visualizations == ['resultscount', 'termfrequency']
    assert field.visualization_sort == 'key'
    assert field.es_mapping['type'] == 'integer'
    assert field.hidden == False
    assert field.sortable == True
    assert field.searchable == False


def test_parse_float_field(float_field_json):
    data = _parse_field(float_field_json)
    field = Field(**data)
    assert field.name == 'ocr_confidence'
    assert field.display_type == 'float'
    assert field.search_filter == {}
    assert field.results_overview == False
    assert field.csv_core == False
    assert field.search_field_core == False
    assert field.visualizations == []
    assert field.es_mapping['type'] == 'float'
    assert field.hidden == False
    assert field.sortable == False
    assert field.searchable == False
    assert field.downloadable == True


def test_parse_date_field(date_field_json):
    data = _parse_field(date_field_json)
    field = Field(**data)
    assert field.name == 'date'
    assert field.display_type == 'date'
    assert field.search_filter['name'] == 'DateFilter'
    assert field.results_overview == True
    assert field.csv_core == True
    assert field.search_field_core == False
    assert field.visualizations == ['resultscount', 'termfrequency']
    assert field.es_mapping['type'] == 'date'
    assert field.hidden == False
    assert field.sortable == True
    assert field.searchable == False


def test_parse_boolean_field(boolean_field_json):
    data = _parse_field(boolean_field_json)
    field = Field(**data)
    assert field.name == 'author_known'
    assert field.display_type == 'boolean'
    assert field.search_filter['name'] == 'BooleanFilter'
    assert field.results_overview == False
    assert field.csv_core == False
    assert field.search_field_core == False
    assert field.visualizations == ['resultscount', 'termfrequency']
    assert field.es_mapping['type'] == 'boolean'
    assert field.hidden == False
    assert field.sortable == False
    assert field.searchable == False


def test_parse_geo_field(geo_field_json):
    data = _parse_field(geo_field_json)
    field = Field(**data)
    assert field.name == 'location'
    assert field.display_type == 'geo_point'
    assert field.search_filter == {}
    assert field.results_overview == False
    assert field.csv_core == False
    assert field.search_field_core == False
    assert field.visualizations == []
    assert field.es_mapping['type'] == 'geo_point'
    assert field.hidden == False
    assert field.sortable == False
    assert field.searchable == False


_documentation = '''This is a test corpus.

You can use it for testing!
'''

def test_parse_documentation(db, json_mock_corpus, json_corpus_definition):
    json_corpus_definition['documentation'] = {
        'general': _documentation,
        'license': 'Do whatever you want',
    }
    data = {
        'definition': json_corpus_definition,
        'active': True,
    }

    serializer = CorpusJSONDefinitionSerializer(data=data)
    assert serializer.is_valid()
    serializer.update(json_mock_corpus, serializer.validated_data)

    pages = CorpusDocumentationPage.objects.filter(
        corpus_configuration__corpus=json_mock_corpus
    )
    assert pages.count() == 2

    page = pages.get(
        type=CorpusDocumentationPage.PageType.GENERAL
    )
    assert page.content == _documentation
