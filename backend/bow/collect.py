from typing import Iterable, Tuple, Dict, Any, Optional
from elasticsearch import Elasticsearch

from addcorpus.models import Corpus, FieldDisplayTypes
from es.client import elasticsearch
from es.search import hits
from visualization.query import MATCH_ALL
from visualization.termvectors import request_termvectors_batched, get_terms


def content_fields(corpus: Corpus) -> Iterable[Tuple[str, Optional[str]]]:
    fields = corpus.configuration.fields.filter(
        display_type=FieldDisplayTypes.TEXT_CONTENT
    ).exclude(
        name__contains=':', # exclude programmatically generated fields
    )
    for field in fields:
        multifield_names = [None]
        multifields = field.es_mapping.get('fields', {})
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
    body = query | { 'index': index, 'allow_no_indices': False, 'sort': ['_doc'], 'size': 1000, }
    result = client.search(**body)
    docs = hits(result)
    while len(docs):
        yield from docs
        last = docs[-1]
        body = body | { 'search_after': last['sort'] }
        result = client.search(**body)
        docs = hits(result)


def collect_tokens(
    corpus: Corpus, index_name: str, threshold=0,
) -> Iterable[Tuple[str, Dict[str, int], Dict[str, Any], str]]:
    client = elasticsearch(corpus)
    docs = custom_scan(client, index_name, MATCH_ALL)
    fields = list(content_fields(corpus))
    field_names = [name for name, _ in fields]
    meta_field_names = list(metadata_fields(corpus))
    for hit, vectors in request_termvectors_batched(docs, client, True, field_names):
        metadata = {
            field: value for field, value in hit['_source'].items()
            if field in meta_field_names
        }
        for name, _multifields in fields:
            terms = get_terms(vectors, name)
            if terms:
                counts = {
                    term: {
                        ':count': data['term_freq'],
                        ':total_count': data['ttf'],
                    }
                    for term, data in terms.items()
                    if data['ttf'] >= threshold
                }
                yield name, counts, metadata, hit['_id']


def token_docs(corpus: Corpus, index_name: str, threshold=0):
    iterator = collect_tokens(corpus, index_name, threshold=threshold)
    for text_field, term_counts, metadata, doc_id in iterator:
        for term, term_count_data in term_counts.items():
            data = {
                ':token': term,
                ':doc_id': doc_id
            }
            content = {text_field: term}
            yield data | content | term_count_data | metadata
