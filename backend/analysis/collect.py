from typing import Iterable, Tuple, Dict, Any, Optional
from elasticsearch import Elasticsearch

from addcorpus.models import Corpus, FieldDisplayTypes
from es.client import elasticsearch
from es.models import Index
from es.search import hits
from visualization.query import MATCH_ALL
from visualization.termvectors import request_termvectors_batched, term_counts
from analysis.index_utils import content_field_name

def content_fields(corpus: Corpus) -> Iterable[Tuple[str, Optional[str]]]:
    fields = corpus.configuration.fields.filter(display_type=FieldDisplayTypes.TEXT_CONTENT)
    for field in fields:
        multifield_names = [None]
        multifields = field.es_mapping.get('fields')
        if 'clean' in multifields:
            multifield_names.append('clean')
        if 'stemmed' in multifields:
            multifield_names.append('stemmed')
        yield field.name, multifield_names


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


def collect_tokens(
    corpus: Corpus, index_name: str
) -> Iterable[Tuple[str, Dict[str, int], Dict[str, Any], str]]:
    client = elasticsearch(corpus)
    docs = custom_scan(client, index_name, MATCH_ALL)
    fields = list(content_fields(corpus))
    field_names = [name for name, _ in fields]
    meta_field_names = list(metadata_fields(corpus))
    for hit, vectors in request_termvectors_batched(docs, client, False, field_names):
        metadata = {
            field: value for field, value in hit['_source'].items()
            if field in meta_field_names
        }
        for name, multifields in fields:
            counts = term_counts(vectors, name)
            yield name, counts, metadata, hit['_id']


def token_docs(corpus: Corpus, index_name: str):
    iterator = collect_tokens(corpus, index_name)
    for field, term_counts, metadata, doc_id in iterator:
        for term, count in term_counts.items():
            data = {':token': term, ':count': count, ':doc_id': doc_id}
            content = {field: term}
            yield data | content | metadata
