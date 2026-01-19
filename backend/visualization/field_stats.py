from es.client import elasticsearch
from es.search import total_hits, search
from addcorpus.models import Corpus, CorpusConfiguration
from visualization.query import MATCH_ALL

def count_field(es_client, corpus_name, fieldname):
    '''
    The absolute of documents that has a value for this field
    '''

    body = {'query': {'exists': {'field': fieldname}}}
    result = search(
        corpus_name=corpus_name,
        query_model=body,
        client=es_client,
        size=0,
        track_total_hits=True,
    )

    return total_hits(result)


def count_total(es_client, corpus_name):
    '''
    The total number of documents in the corpus
    '''

    result = search(
        corpus_name=corpus_name,
        client=es_client,
        query_model=MATCH_ALL,
        size=0,
        track_total_hits=True,
    )
    return total_hits(result)

def report_coverage(corpus_name):
    '''
    Returns a dict with the ratio of documents that have a value for each field in the corpus
    '''

    es_client = elasticsearch(corpus_name)
    corpus_conf = CorpusConfiguration.objects.get(corpus__name=corpus_name)

    total = count_total(es_client, corpus_name)

    return {
        field.name: count_field(es_client, corpus_name, field.name) / total
        for field in corpus_conf.fields.all()
    }


