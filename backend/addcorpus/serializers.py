from typing import Dict

from addcorpus.constants import CATEGORIES
from addcorpus.documentation import render_documentation_context
from addcorpus.json_corpora.export_json import export_json_corpus
from addcorpus.json_corpora.import_json import import_json_corpus
from addcorpus.models import (Corpus, CorpusConfiguration, CorpusDataFile,
                              CorpusDocumentationPage, Field)
from addcorpus.permissions import can_edit
from django.core.files import File
from langcodes import Language, standardize_tag
from rest_framework import serializers
from os import path


class NonEmptyJSONField(serializers.JSONField):
    '''
    JSON field serialiser that converts empty dicts `{}`
    to `None`/null values
    '''

    def to_representation(self, value):
        data = super().to_representation(value)
        # do not return empty dicts
        if data:
            return data

class FieldSerializer(serializers.ModelSerializer):
    search_filter = NonEmptyJSONField()
    class Meta:
        model = Field
        fields = [
            'name',
            'display_name',
            'display_type',
            'description',
            'search_filter',
            'results_overview',
            'csv_core',
            'search_field_core',
            'visualizations',
            'visualization_sort',
            'es_mapping',
            'indexed',
            'hidden',
            'required',
            'sortable',
            'searchable',
            'downloadable',
            'language',
        ]


class LanguageField(serializers.CharField):
    def to_representation(self, value):
        if value:
            language = Language.make(standardize_tag(value))
            return language.display_name()
        else:
            return 'Unknown'

class PrettyChoiceField(serializers.ChoiceField):
    '''
    Variation on ChoiceField that serialises
    the display name rather than the internal name
    '''

    def to_representation(self, value):
        key = super().to_representation(value)
        return self.choices[key]

    def to_internal_value(self, data):
        # If the data provides a display name, get the corresponding key.
        # The browsable API sends keys instead of labels; use the original data if no
        # matching label is found.
        value = next(
            (key for (key, label) in self.choices.items() if label == data),
            data
        )
        return super().to_internal_value(value)

class CorpusConfigurationSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, source='visible_fields')
    languages = serializers.ListField(child=LanguageField())
    category = PrettyChoiceField(choices=CATEGORIES)
    default_sort = NonEmptyJSONField()

    class Meta:
        model = CorpusConfiguration
        fields = [
            'allow_image_download',
            'category',
            'description',
            'document_context',
            'languages',
            'min_year',
            'max_year',
            'scan_image_type',
            'title',
            'word_models_present',
            'default_sort',
            'language_field',
            'fields',
            'has_named_entities',
        ]

class CorpusSerializer(serializers.ModelSerializer):
    configuration = CorpusConfigurationSerializer(read_only=True)
    editable = serializers.SerializerMethodField()

    class Meta:
        model = Corpus
        fields = ['id', 'name', 'configuration', 'editable']


    def get_editable(self, instance):
        if request := self.context.get('request'):
            user = request.user
            return can_edit(user, instance)


    def to_representation(self, instance: Corpus):
        # flatten representation: corpus configuration
        # data is moved to root dict
        data = super().to_representation(instance)
        conf_data = data.pop('configuration')
        data.update(conf_data)
        return data


class DocumentationTemplateField(serializers.CharField):
    '''
    Serialiser for the contents of documentation pages.

    Pages are Templates written in markdown.
    '''

    def to_representation(self, value):
        content = super().to_representation(value)
        return render_documentation_context(content)


class CorpusDocumentationPageSerializer(serializers.ModelSerializer):
    type = PrettyChoiceField(choices = CorpusDocumentationPage.PageType.choices)
    index = serializers.IntegerField(source='page_index', read_only=True)
    content = DocumentationTemplateField(read_only=True)
    corpus = serializers.SlugRelatedField(
        source='corpus_configuration',
        queryset=CorpusConfiguration.objects.all(),
        slug_field='corpus__name',
    )

    class Meta:
        model = CorpusDocumentationPage
        fields = ['id', 'corpus', 'type', 'content', 'index']


class JSONDefinitionField(serializers.Field):
    def get_attribute(self, instance: Corpus):
        return instance

    def to_representation(self, value: Corpus) -> Dict:
        return export_json_corpus(value)

    def to_internal_value(self, data: Dict) -> Dict:
        return import_json_corpus(data)


class CorpusJSONDefinitionSerializer(serializers.ModelSerializer):
    definition = JSONDefinitionField()
    has_image = serializers.BooleanField(source='configuration.image', read_only=True)
    has_complete_data = serializers.SerializerMethodField()

    class Meta:
        model = Corpus
        fields = ['id', 'active', 'definition',
                  'owner', 'has_image', 'has_complete_data']
        read_only_fields = ['id']

    def get_has_complete_data(self, obj: Corpus):
        '''Corpus should have exactly one file, that is confirmed'''
        confirmed_exists = CorpusDataFile.objects.filter(
            corpus=obj, confirmed=True).exists()
        unconfirmed_exists = CorpusDataFile.objects.filter(
            corpus=obj, confirmed=False).exists()
        return confirmed_exists and not unconfirmed_exists

    def create(self, validated_data: Dict):
        definition_data = validated_data.get('definition')
        configuration_data = definition_data.pop('configuration')
        fields_data = configuration_data.pop('fields')
        documentation_data = configuration_data.pop('documentation_pages')

        corpus = Corpus.objects.create(**definition_data)
        configuration = CorpusConfiguration.objects.create(corpus=corpus, **configuration_data)
        for i, field_data in enumerate(fields_data):
            Field.objects.create(
                corpus_configuration=configuration, position=i, **field_data
            )

        if validated_data.get('owner'):
            user = validated_data.get('owner')
            corpus.owner = user
            corpus.save()

        if validated_data.get('active') == True:
            corpus.active = True
            corpus.save()

        for page in documentation_data:
            CorpusDocumentationPage.objects.create(
                corpus_configuration=configuration,
                type=page['type'],
                content=page['content'],
            )

        return corpus

    def update(self, instance: Corpus, validated_data: Dict):
        definition_data = validated_data.get('definition')
        configuration_data = definition_data.pop('configuration')
        fields_data = configuration_data.pop('fields')
        documentation_data = configuration_data.pop('documentation_pages')

        corpus = Corpus(
            pk=instance.pk, date_created=instance.date_created, owner=instance.owner,
            **definition_data,
        )
        corpus.save()

        configuration, _ = CorpusConfiguration.objects.get_or_create(corpus=corpus)
        for attr in configuration_data:
            setattr(configuration, attr, configuration_data[attr])
        configuration.save()

        for i, field_data in enumerate(fields_data):
            try:
                field = Field.objects.get(
                    corpus_configuration=configuration, name=field_data['name'])
            except Field.DoesNotExist:
                field = Field(corpus_configuration=configuration,
                              name=field_data['name'])
            for attr in field_data:
                setattr(field, attr, field_data[attr])
            field.position = i
            field.save()

        configuration.fields.exclude(name__in=(f['name'] for f in fields_data)).delete()

        if validated_data.get('active') == True:
            corpus.active = True
            corpus.save()

        configuration.documentation_pages.exclude(
            type__in=(page['type'] for page in documentation_data)).delete()
        for page in documentation_data:
            match = CorpusDocumentationPage.objects.filter(
                corpus_configuration=configuration,
                type=page['type'],
            )

            if match.exists():
                match.update(content=page['content'])
            else:
                CorpusDocumentationPage.objects.create(
                    corpus_configuration=configuration,
                    type=page['type'],
                    content=page['content'],
                )

        return corpus


class DataFileField(serializers.FileField):
    def to_representation(self, value: File) -> Dict:
        return path.basename(value.name)

    def to_internal_value(self, data):
        return super().to_internal_value(data)


class CorpusDataFileSerializer(serializers.ModelSerializer):
    file = DataFileField()
    original_filename = serializers.CharField(read_only=True)
    csv_info = serializers.JSONField(read_only=True)

    class Meta:
        model = CorpusDataFile
        fields = ('id', 'corpus', 'file', 'created', 'is_sample',
                  'confirmed', 'original_filename', 'csv_info')

    def validate(self, data):
        if file := data.get('file'):
            data['original_filename'] = file.name
        return data
