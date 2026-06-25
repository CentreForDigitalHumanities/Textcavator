from typing import Iterable, Tuple, Dict, Any, Optional
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


def collect_tokens(corpus: Corpus, index: Index) -> Iterable[Tuple[str, Dict[str, int], Dict[str, Any]]]:
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


def token_field_name(field_name: str, multifield: Optional[str] = None,  size: int = 1):
    if multifield:
        return ':'.join([field_name, multifield, size])
    return ':'.join([field_name, size])


def token_docs(corpus: Corpus, index: Index):
    iterator = collect_tokens(corpus, index)
    for field, term_counts, metadata in iterator:
        token_field = token_field_name(field, None, 1)
        for term, count in term_counts.items():
            for count in range(count):
                yield { token_field: term } | metadata
