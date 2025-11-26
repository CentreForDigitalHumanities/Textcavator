import os

from addcorpus.json_corpora.validate import corpus_schema
from addcorpus.models import (Corpus, CorpusConfiguration, CorpusDataFile,
                              CorpusDocumentationPage)
from addcorpus.permissions import (CanEditCorpus, CanEditOrSearchCorpus,
                                   CanSearchCorpus, corpus_name_from_request,
                                   editable_corpora, searchable_condition,
                                   searchable_corpora)
from addcorpus.python_corpora.load_corpus import corpus_dir
from addcorpus.serializers import (CorpusDataFileSerializer,
                                   CorpusDocumentationPageSerializer,
                                   CorpusJSONDefinitionSerializer,
                                   CorpusSerializer)
from addcorpus.utils import clear_corpus_image
from django.conf import settings
from django.db.models import Q
from django.http.response import FileResponse
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView


class CorpusView(viewsets.ReadOnlyModelViewSet):
    '''
    List all available corpora
    '''

    serializer_class = CorpusSerializer

    def get_queryset(self):
        return searchable_corpora(self.request.user).order_by('-date_created')


class CorpusDocumentationPageViewset(viewsets.ReadOnlyModelViewSet):
    '''
    Markdown documentation pages for corpora.
    '''

    permission_classes = [CanEditOrSearchCorpus]
    serializer_class = CorpusDocumentationPageSerializer

    def corpus_from_object(self, obj: CorpusDocumentationPage) -> Corpus:
        return obj.corpus_configuration.corpus


    def get_queryset(self):
        condition = searchable_condition(self.request.user)

        queried_corpus = self.request.query_params.get('corpus')
        if queried_corpus:
            condition &= Q(name=queried_corpus)

        corpora = Corpus.objects.filter(condition)
        return CorpusDocumentationPage.objects.filter(
            corpus_configuration__corpus__in=corpora
        )


class CorpusImageView(APIView):
    '''
    Return the image for a corpus.
    '''

    permission_classes = [CanEditOrSearchCorpus]

    def get_object(self):
        corpus_name = corpus_name_from_request(self.request)
        return CorpusConfiguration.objects.get(corpus__name=corpus_name)

    def corpus_from_object(self, obj: CorpusConfiguration) -> Corpus:
        return obj.corpus

    def get(self, request, *args, **kwargs):
        try:
            corpus_config = self.get_object()
        except:
            raise NotFound('Corpus does not exist')

        self.check_object_permissions(request, corpus_config)

        if corpus_config.image:
            path = corpus_config.image.path
        else:
            path = settings.DEFAULT_CORPUS_IMAGE

        return FileResponse(open(path, 'rb'))


    def put(self, request, *args, **kwargs):
        corpus_config = self.get_object()

        clear_corpus_image(corpus_config.corpus)

        file = request.FILES['file']
        corpus_config.image = file
        name, ext = os.path.splitext(corpus_config.image.name)
        corpus_config.image.name = corpus_config.corpus.name + ext
        corpus_config.save()

        return Response('Image saved', HTTP_200_OK)


    def delete(self, request, *args, **kwargs):
        corpus_config = self.get_object()
        clear_corpus_image(corpus_config.corpus)

        return Response('Image deleted', HTTP_200_OK)


class CorpusDocumentView(APIView):
    '''
    Return a file for a corpus - e.g. extra metadata.
    '''

    permission_classes = [CanSearchCorpus]

    def get(self, request, *args, **kwargs):
        corpus = Corpus.objects.get(corpus_name_from_request(request))
        if not corpus.has_python_definition:
            raise NotFound()
        path = os.path.join(corpus_dir(corpus.name), 'documents', kwargs['filename'])
        if not os.path.isfile(path):
            raise NotFound()
        return FileResponse(open(path, 'rb'))


class CorpusDefinitionViewset(viewsets.ModelViewSet):
    permission_classes = [CanEditCorpus]
    serializer_class = CorpusJSONDefinitionSerializer

    def corpus_from_object(self, obj: Corpus) -> Corpus:
        return obj

    def get_queryset(self):
        return editable_corpora(self.request.user)


    def perform_create(self, serializer):
        '''Overwrites ModelViewSet.perform_create
        Auto-assigns the authenticated user on creation'''
        return serializer.save(owner=self.request.user)


class CorpusDataFileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CanEditCorpus]
    serializer_class = CorpusDataFileSerializer

    def corpus_from_object(self, obj: CorpusDataFile) -> Corpus:
        return obj.corpus


    def get_queryset(self):
        queryset = CorpusDataFile.objects.filter(
            corpus__in=editable_corpora(self.request.user)
        )

        corpus = self.request.query_params.get('corpus')
        if corpus:
            queryset = queryset.filter(corpus=corpus)

        samples = self.request.query_params.get('samples', False)
        if samples:
            queryset = queryset.filter(is_sample=True)

        return queryset.order_by('created')

class CorpusDefinitionSchemaView(APIView):
    '''
    View the JSON schema for corpus definitions
    '''

    def get(self, request, *args, **kwargs):
        schema = corpus_schema()
        return Response(schema, HTTP_200_OK)
