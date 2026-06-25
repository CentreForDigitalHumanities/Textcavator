from elasticsearch.helpers import scan

from addcorpus.models import Corpus, FieldDisplayTypes
from es.client import elasticsearch
from es.models import Index
from visualization.query import MATCH_ALL
from visualization.termvectors import request_termvectors_batched, term_counts


def content_fields(corpus: Corpus):
    return [
        field for field in corpus.configuration.fields
        if field.display_type == FieldDisplayTypes.TEXT_CONTENT
    ]

def metadata_fields(corpus: Corpus):
    return [
        field for field in corpus.configuration.fields
        if field.display_type != FieldDisplayTypes.TEXT_CONTENT
    ]


def collect_tokens(corpus: Corpus, index: Index):
    client = elasticsearch(corpus)
    query = MATCH_ALL | { 'index': index.name, 'allow_no_indices': False }
    docs = scan(client, query)
    # TODO: handle multifields
    content_field_names = [field.name for field in content_fields(corpus)]
    meta_field_names = [field.name for field in metadata_fields(corpus)]
    for hit, vectors in request_termvectors_batched(docs, client, False, content_field_names):
        metadata = {
            field: value for field, value in hit['_source'].items()
            if field in meta_field_names
        }
        for field in content_field_names:
            counts = term_counts(vectors, field)
            yield field, counts, metadata
