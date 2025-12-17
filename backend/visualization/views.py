from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException, ParseError, ValidationError
from visualization import tasks
import logging
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from addcorpus.permissions import CanSearchCorpus
from tag.permissions import CanSearchTags
from visualization.field_stats import report_coverage
from addcorpus.permissions import corpus_name_from_request
from api.utils import check_json_keys

logger = logging.getLogger()

TERM_FREQUENCY_SIZE_LIMIT = 10500
'''Limit for the term frequency graph. Size is currently set in the frontend, this is
only to prevent overuse. The limit is slightly over what the frontend should request
to prevent errors due to rounding in each bin.
'''


class WordcloudView(APIView):
    '''
    Most frequent terms for a small batch of results
    '''

    permission_classes = [CanSearchCorpus, CanSearchTags]

    def post(self, request, *args, **kwargs):
        check_json_keys(request, ['corpus', 'es_query', 'field', 'size'])
        wordcloud_limit = settings.WORDCLOUD_LIMIT
        if request.data['size'] > wordcloud_limit:
            raise ParseError(
                detail=f'size exceeds {wordcloud_limit} documents')

        try:
            # no need to run async: we will use the result directly
            word_counts = tasks.get_wordcloud_data(request.data)
            return Response(word_counts)
        except Exception as e:
            logger.error(e)
            raise APIException(detail='could not generate word cloud data')


class MapView(APIView):
    '''
    Retrieve documents with geo_field coordinates.
    '''

    permission_classes = [CanSearchCorpus]

    def post(self, request, *args, **kwargs):
        check_json_keys(request, ['corpus', 'es_query', 'field'])
        try:
            # no need to run async: we will use the result directly
            documents = tasks.get_geo_data(request.data)
            return Response(documents)
        except Exception as e:
            logger.error(e)
            raise APIException(detail='could not generate geo data')


class MapCentroidView(APIView):
    '''
    Retrieve the centroid of documents with a geo_field for a corpus.
    '''

    permission_classes = [CanSearchCorpus]

    def post(self, request, *args, **kwargs):
        check_json_keys(request, ['corpus', 'field'])
        try:
            center = tasks.get_geo_centroid(request.data)
            return Response(center)
        except Exception as e:
            logger.error(e)
            raise APIException(detail='Could not retrieve geo centroid')

class NgramView(APIView):
    '''
    Schedule a task to retrieve ngrams containing the search term, or collocates
    of the search term.
    '''

    permission_classes = [CanSearchCorpus, CanSearchTags]

    def post(self, request, *args, **kwargs):
        check_json_keys(request, [
            'es_query', 'corpus_name', 'field', 'ngram_size', 'term_position',
            'freq_compensation', 'subfield', 'max_size_per_interval',
            'number_of_ngrams', 'date_field'
        ])

        try:
            chord = tasks.ngram_data_tasks(request.data)()
            subtasks = [chord, *chord.parent.children]
            return Response({'task_ids': [task.id for task in subtasks]})
        except Exception as e:
            logger.error(e)
            raise APIException(detail='Could not set up ngram generation.')


class DateTermFrequencyView(APIView):
    '''
    Schedule a task to retrieve term frequency
    compared by a date field
    '''

    permission_classes = [CanSearchCorpus, CanSearchTags]

    def post(self, request, *args, **kwargs):
        check_json_keys(
            request, ['es_query', 'corpus_name', 'field_name', 'bins'])

        bins = request.data['bins']
        for bin in  bins:
            for key in ['start_date', 'end_date', 'size']:
                if not key in bin:
                    raise ParseError(
                        detail=f'key {key} is not present for all bins in request data')

        if sum(bin['size'] for bin in bins) > TERM_FREQUENCY_SIZE_LIMIT:
            raise ValidationError(detail='Maximum size exceeded')

        try:
            group = tasks.timeline_term_frequency_tasks(
                request.data).apply_async()
            subtasks = group.children
            return Response({'task_ids': [task.id for task in subtasks]})
        except Exception as e:
            logger.error(e)
            raise APIException('Could not set up term frequency generation.')


class AggregateTermFrequencyView(APIView):
    '''
    Schedule a task to retrieve term frequency
    compared by a keyword field
    '''

    permission_classes = [CanSearchCorpus, CanSearchTags]

    def post(self, request, *args, **kwargs):
        check_json_keys(
            request, ['es_query', 'corpus_name', 'field_name', 'bins'])

        bins = request.data['bins']
        for bin in bins:
            for key in ['field_value', 'size']:
                if not key in bin:
                    raise ParseError(
                        detail=f'key {key} is not present for all bins in request data')

        if sum(bin['size'] for bin in bins) > TERM_FREQUENCY_SIZE_LIMIT:
            raise ValidationError(detail='Maximum size exceeded')

        try:
            group = tasks.histogram_term_frequency_tasks(
                request.data).apply_async()
            subtasks = group.children
            return Response({'task_ids': [task.id for task in subtasks]})
        except Exception as e:
            logger.error(e)
            raise APIException('Could not set up term frequency generation.')


class FieldCoverageView(APIView):
    '''
    Get the coverage of each field in a corpus
    '''

    permission_classes = [CanSearchCorpus]

    def get(self, request, *args, **kwargs):
        corpus = corpus_name_from_request(request)
        report = report_coverage(corpus)
        return Response(report)
