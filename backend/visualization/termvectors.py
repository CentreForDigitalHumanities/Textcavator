from typing import List, Dict, Any, Optional, Iterable
import re
import itertools

from elasticsearch import Elasticsearch
from textdistance import damerau_levenshtein
from es.client import elasticsearch

from visualization.simple_query_string import collect_terms

def request_termvectors_batched(
    hits: Iterable[Dict], client: Elasticsearch, term_statistics: bool,
    fields: List[str],
) -> Iterable[Dict]:
    '''
    Request term vectors for each hit in search results.
    Uses mtermvectors endpoint to make batched requests.
    '''
    batched_hits = itertools.batched(hits, 100)
    for batch in batched_hits:
        result = client.mtermvectors(
            docs=[
                { '_index': doc['_index'], '_id': doc['_id'] }
                for doc in batch
            ],
            term_statistics=term_statistics,
            fields=fields,
        )
        yield from result.body['docs']

def get_terms(termvector_result, field: str) -> Optional[Dict[str, Dict]]:
    termvectors = termvector_result['term_vectors']
    if field in termvectors:
        terms = termvectors[field]['terms']
        return terms

def get_tokens(terms: Dict[str, Dict], sort=True) -> List[Dict[str, Any]]:
    if not terms:
        return []

    all_tokens = [token for term in terms for token in list_tokens(term, terms[term])]

    if sort:
        sorted_tokens = sorted(all_tokens, key=lambda token: token['position'])
        return sorted_tokens

    return all_tokens

def list_tokens(term, details):
    ttf = details['ttf'] if 'ttf' in details else 0
    positions = [token['position'] for token in details['tokens']]

    return [ {
        'position': position,
        'term': term,
        'ttf': ttf
        }
        for position in positions
    ]

def token_matches(tokens, query_text, index, field, es_client = None):
    """
    Iterates over the matches in list of tokens (i.e. the output of `list_tokens`) for a query.

    Each iteration is a tuple wit the start index (in tokens), stop index of the match, and term
    """
    analyzed_query = analyze_query(query_text, index, field, es_client)

    for i in range(len(tokens)):
        for component in analyzed_query:
            if len(component) + i <= len(tokens):
                if all(terms_match(tokens[i + j]['term'], component[j]) for j in range(len(component))):
                    start = i
                    stop = i + len(component)
                    content = ' '.join([tokens[ind]['term'] for ind in range(start, stop)])
                    yield start, stop, content


def terms_match(term, query_term: str):
    """
    Whether a term in the content matches a term from the query.

    Query terms can include `.*` wildcards, or do fuzzy search with `~{edit-distance}` at the end.
    The edit distance is measured as damerau-levenshtein, since this is used by elasticsearch as well.
    """

    # handle wildcard
    if '.*' in query_term:
        return re.match(query_term, term) != None

    # handle fuzzy match
    fuzzy_match = re.search(r'(\S+)~(\d+)$', query_term)
    if fuzzy_match:
        max_distance = int(fuzzy_match.group(2))
        clean_query_term = fuzzy_match.group(1)
        distance = damerau_levenshtein(term, clean_query_term)
        return distance <= max_distance

    return term == query_term

def analyze_query(query_text, index, field, es_client = None):
    """
    Tokenise a query and apply the language analyser from this field in the index.
    """

    if not es_client:
        es_client = elasticsearch(index)

    components = collect_terms(query_text)
    analyzed_components = [analyze_query_component(component, index, field, es_client) for component in components]

    nonempty = list(filter(None, analyzed_components))

    return nonempty

def analyze_query_component(component_text, index, field, es_client):
    analyzed = es_client.indices.analyze(index=index, text=component_text, field=field)

    tokens = [token['token'] for token in analyzed['tokens']]


    if len(component_text.split()) == 1:
        # for single-word tokens, add exceptions for wildcard and fuzzy match
        # everything outside quotes is passed per word

        wildcard_match = re.search(r'\*$', component_text)
        if wildcard_match:
            return [tokens[0] + '.*'] # return re with wildcard

        fuzzy_match = re.search(r'~(\d+)$', component_text)
        if fuzzy_match:
            digits = fuzzy_match.group(1)
            return [tokens[0] + '~' + digits]

    return tokens


