import math
from typing import Callable, Dict, Any, Optional, List
import re
from addcorpus.models import CorpusConfiguration, Field
from datetime import datetime
from es.search import total_hits, search
from es.client import elasticsearch
from copy import deepcopy
from visualization import query, termvectors, simple_query_string
from es import download

DEFAULT_SIZE = 100
ESTIMATE_WINDOW = 5

def parse_datestring(datestring):
    return datetime.strptime(datestring, '%Y-%m-%d')

def get_date_term_frequency(es_query, corpus, field, start_date_str, end_date_str=None, size=DEFAULT_SIZE, include_query_in_result=False):

    start_date = parse_datestring(start_date_str)
    end_date = parse_datestring(end_date_str) if end_date_str else None

    date_filter = query.make_date_filter(start_date, end_date, date_field = field)
    es_query = query.add_filter(es_query, date_filter)
    query_text = query.get_query_text(es_query)

    match_count, doc_count, token_count = get_term_frequency(es_query, corpus, size)

    data = {
        'key': start_date_str,
        'key_as_string': start_date_str,
        'total_doc_count': doc_count,
        'match_count': match_count,
        'token_count': token_count,
    }

    if include_query_in_result:
        data['query'] = query_text

    return data

def extract_data_for_term_frequency(corpus, es_query):
    fields = _term_frequency_search_fields(corpus, es_query)
    has_length_count = lambda field: 'fields' in field.es_mapping and 'length' in field.es_mapping['fields']
    include_token_count = all(has_length_count(field) for field in fields)
    fieldnames = [field.name for field in fields]

    if include_token_count:
        token_count_aggregators = {
            'token_count_' + field.name: {
                'sum': {
                    'field': field.name + '.length'
                }
            }
            for field in fields
        }
    else:
        token_count_aggregators = None

    return fieldnames, token_count_aggregators

def _term_frequency_search_fields(corpus, es_query) -> List[Field]:
    '''
    Select search fields for term frequency analysis.

    Selects either the fields selected in the query, or all text fields in the corpus.
    '''
    corpus_conf = CorpusConfiguration.objects.get(corpus__name=corpus)
    all_fields = corpus_conf.fields.all()
    search_fields = query.get_search_fields(es_query)
    if search_fields:
        fields = list(filter(lambda field: field.name in search_fields, all_fields))
    else:
        fields = list(filter(lambda field: field.es_mapping['type'] == 'text', all_fields))

    return fields


def get_match_count(es_client, es_query, corpus, size, fieldnames):
    es_query = query.set_search_fields(es_query, fieldnames)
    found_hits, total_results = download.scroll(corpus=corpus,
        query_model=es_query,
        download_size=size,
        client=es_client,
        source=[],
        explain=True,
    )

    query_text = query.get_query_text(es_query)
    terms = simple_query_string.collect_terms(query_text)
    prefix_query = ' '.join(filter(requires_termvectors_analysis, terms))

    matches = [
        count_matches_in_document(hit, prefix_query, fieldnames, es_client)
        for hit in found_hits
    ]

    n_matches = sum(matches)
    skipped_docs = total_results - len(matches)
    if not skipped_docs:
        return n_matches
    match_count = n_matches + estimate_skipped_count(matches, skipped_docs)
    return match_count


def requires_termvectors_analysis(term: str) -> bool:
    return simple_query_string.is_prefix(term) and not simple_query_string.is_negated(term)


def estimate_skipped_count(matches, skipped_docs: int) -> int:
    mean_last_matches = sum(matches[-ESTIMATE_WINDOW:]) / ESTIMATE_WINDOW
    # we estimate that skipped contain matches linearly decrease
    # from average in ESTIMATE_WINDOW to 1
    estimate_skipped = int(math.ceil(mean_last_matches - 1) * skipped_docs / 2) + skipped_docs
    return estimate_skipped


def count_matches_in_document(hit, prefix_query: Optional[str], search_fields, es_client):
    '''
    Count matches of a query in a document.

    Will use the explain API if possible, which is faster.

    Because this API will not count prefix queries, `prefix_query` specificies the
    section of the query that should be counted using termvectors. Will do nothing
    if this is empty.
    '''
    if prefix_query:
        # If the query contains a prefix query, use termvectors to get matches
        # for it.
        prefix_matches = count_matches_from_termvectors(
            hit['_id'], hit['_index'], search_fields, prefix_query, es_client
        )
        # Use explanation for other terms in the query (this is faster and more
        # accurate if the query includes certain other operators)
        rest_matches = count_matches_from_explanation(hit)
        return prefix_matches + rest_matches

    return count_matches_from_explanation(hit)


def count_matches_from_explanation(hit) -> int:
    '''Count matches of a query in a document using the explain API'''
    explanation = hit['_explanation']
    matches = find_recursive(explanation, is_description)
    total = sum(match['value'] for match in matches)
    return total


def is_description(doc: Dict):
    if description := doc.get('description'):
        if re.match(r'freq,|phraseFreq=', description):
            return True
    return False


def find_recursive(doc: Any, predicate: Callable):
    if isinstance(doc, dict):
        if predicate(doc):
            yield doc

        for value in doc.values():
            for match in find_recursive(value, predicate):
                yield match

    if isinstance(doc, list):
        for item in doc:
            for match in find_recursive(item, predicate):
                yield match


def count_matches_from_termvectors(id, index, fieldnames, query_text, es_client):
    '''
    Count matches of a query in a document using the termvectors API
    '''
    # get the term vectors for the hit
    result = es_client.termvectors(index=index, id=id, fields = fieldnames)

    matches = 0

    for field in fieldnames:
        terms = termvectors.get_terms(result, field)
        tokens = termvectors.get_tokens(terms, sort = False)
        matches += sum(1 for _ in termvectors.token_matches(tokens, query_text, index, field, es_client))

    return matches


def get_total_docs_and_tokens(es_client, query, corpus, token_count_aggregators):
    if token_count_aggregators:
        query['aggs'] = token_count_aggregators

    results = search(
        corpus_name = corpus,
        query_model = query,
        size = 0, # don't include documents
        track_total_hits = True
    )

    total_doc_count = total_hits(results)

    if token_count_aggregators:
        token_count = int(sum(
            results['aggregations'][counter]['value']
            for counter in results['aggregations'] if counter.startswith('token_count')
        ))
    else:
        token_count = None

    return total_doc_count, token_count

def get_term_frequency(es_query, corpus, size):
    client = elasticsearch(corpus)

    # field specifications (used for counting hits), and token count aggregators (for total word count)
    fieldnames, token_count_aggregators = extract_data_for_term_frequency(corpus, es_query)

    # count number of matches
    match_count = get_match_count(client, deepcopy(es_query), corpus, size, fieldnames)

    # get total document count and (if available) token count for bin
    agg_query = query.remove_query(es_query) #remove search term filter
    total_doc_count, token_count = get_total_docs_and_tokens(client, agg_query, corpus, token_count_aggregators)

    return match_count, total_doc_count, token_count

def get_aggregate_term_frequency(es_query, corpus, field_name, field_value, size=DEFAULT_SIZE, include_query_in_result=False):
    # filter for relevant value
    term_filter = query.make_term_filter(field_name, field_value)
    es_query = query.add_filter(es_query, term_filter)
    query_text = query.get_query_text(es_query)

    match_count, doc_count, token_count = get_term_frequency(es_query, corpus, size)

    result = {
        'key': field_value,
        'match_count': match_count,
        'total_doc_count': doc_count,
        'token_count': token_count,
    }

    if include_query_in_result:
        result['query'] = query_text

    return result
