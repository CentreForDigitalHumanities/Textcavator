import logging

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from addcorpus.permissions import CanSearchCorpus
from api.save_query import should_save_query
from addcorpus.models import Corpus
from api.models import Query
from api.api_query import api_query_to_es_query
from es.search import get_index, total_hits, hits
from es.client import elasticsearch
from tag.permissions import CanSearchTags

logger = logging.getLogger(__name__)

def get_query_parameters(request):
        'get query params from a request'

        IGNORE_KEYS = ['tags']

        # extract each query_param with .get, otherwise they return as lists
        return {
            key: request.query_params.get(key)
            for key in request.query_params
            if key not in IGNORE_KEYS
        }

class ForwardSearchView(APIView):
    '''
    Forward search request to elasticsearch search API

    The request may specify:
    - `es_query`: a query for the elasticsearch search API
    https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html
    - `tags`: an array of tag IDs that the results should be filtered on. Multiple tags
    are combined with OR logic: a document must match any of them.

    You can optionally include extra query parameters in the request, which should be valid
    parameters for the elasticsearch API. They will be merged with the query body. E.g.,
    adding `size=100&from=200` as a query parameter will merge `{"size":100, "from": 200}`
    into the query. If you specify a parameter in both the body and as a query parameter,
    the query parameter will be used.
    '''

    permission_classes = [CanSearchCorpus, CanSearchTags]

    def post(self, request, *args, **kwargs):
        corpus_name = kwargs.get('corpus')
        client = elasticsearch(corpus_name)
        index = get_index(corpus_name)

        # combine request json with query parameters (size, scroll)
        api_query = self._extract_api_query(request)
        history_obj = self._save_query_started(request, corpus_name, api_query)

        es_query = api_query_to_es_query(api_query, corpus_name)

        try:
            results = client.search(
                index=index,
                **es_query,
                track_total_hits=True,
            )
        except Exception as e:
            logger.exception(e)
            raise APIException('Search failed')

        if history_obj and results:
            self._save_query_done(history_obj, results)

        return Response(results)

    def _extract_api_query(self, request):
        es_query = {
            **request.data.get('es_query', {}),
            **get_query_parameters(request)
        }
        api_query = {'es_query': es_query}
        if 'tags' in request.data:
            api_query['tags'] = request.data.get('tags')

        return api_query

    def _save_query_started(self, request, corpus_name, api_query):
        es_query = api_query_to_es_query(api_query, corpus_name)
        if should_save_query(request.user, api_query):
            corpus = Corpus.objects.get(name=corpus_name)
            return Query.objects.create(
                user=request.user,
                corpus=corpus,
                query_json=api_query,
            )

    def _save_query_done(self, query, results):
        query.completed = timezone.now()
        query.total_results = total_hits(results)
        query.transferred = len(hits(results))
        query.save()
