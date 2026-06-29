from typing import Iterable, Tuple, Dict, Any, Optional
from elasticsearch.helpers import scan
from elasticsearch import Elasticsearch

from addcorpus.models import Corpus, FieldDisplayTypes
from es.client import elasticsearch
from es.models import Index
from es.search import hits
from visualization.query import MATCH_ALL
from visualization.termvectors import request_termvectors_batched, term_counts


def content_fields(corpus: Corpus) -> Iterable[Tuple[str, Optional[str]]]:
    fields = corpus.configuration.fields.filter(display_type=FieldDisplayTypes.TEXT_CONTENT)
    for field in fields:
        yield field.name, None
        multifields = field.es_mapping.get('fields')
        if 'clean' in multifields:
            yield field.name, 'clean'
        if 'stemmed' in multifields:
            yield field.name, 'stemmed'

def content_field_name(name: str, multifield: Optional[str] = None):
    return f'{name}.{multifield}' if multifield else name

def metadata_fields(corpus: Corpus) -> Iterable[str]:
    return [
        field.name for field in
        corpus.configuration.fields.exclude(
            display_type__in=[FieldDisplayTypes.TEXT_CONTENT, FieldDisplayTypes.TEXT]
        )
    ]


def custom_scan(client: Elasticsearch, index: str, query: Dict):
    body = query | { 'index': index, 'allow_no_indices': False, 'sort': ['_doc'] }
    result = client.search(**body)
    docs = hits(result)
    while len(docs):
        yield from docs
        last = docs[-1]
        body = body | { 'search_after': last['sort'] }
        result = client.search(**body)
        docs = hits(result)


def collect_tokens(corpus: Corpus, index_name: str) -> Iterable[Tuple[str, Optional[str], Dict[str, int], Dict[str, Any]]]:
    client = elasticsearch(corpus)
    docs = custom_scan(client, index_name, MATCH_ALL)
    fields = list(content_fields(corpus))
    field_names = [
        content_field_name(name, multifield)
        for name, multifield in fields
    ]
    meta_field_names = list(metadata_fields(corpus))
    for hit, vectors in request_termvectors_batched(docs, client, False, field_names):
        metadata = {
            field: value for field, value in hit['_source'].items()
            if field in meta_field_names
        }
        for name, multifield in fields:
            counts = term_counts(vectors, content_field_name(name ,multifield))
            yield name, multifield, counts, metadata


def token_field_name(field_name: str, multifield: Optional[str] = None,  size: int = 1):
    if multifield:
        return f'{field_name}:{multifield}:{size}'
    return f'{field_name}:{size}'


def token_docs(corpus: Corpus, index_name: str):
    iterator = collect_tokens(corpus, index_name)
    for field, multifield, term_counts, metadata in iterator:
        token_field = token_field_name(field, multifield, 1)
        for term, count in term_counts.items():
            for count in range(count):
                yield { token_field: term } | metadata
