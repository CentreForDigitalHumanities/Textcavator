from typing import List, Dict, Any, Optional, Iterable

from es.client import elasticsearch
import re
from textdistance import damerau_levenshtein

from visualization.simple_query_string import collect_terms

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
        return _sort_tokens_list(all_tokens)
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

def _sort_tokens_list(tokens: List[Dict]) -> Iterable[Dict]:
    return sorted(tokens, key=lambda token: token['position'])

def token_range_from_list(tokens: List[Dict], start: int, stop: int, sort=True) -> Iterable[Dict]:
    range_tokens = filter(lambda token: start <= token['position'] < stop, tokens)
    if sort:
        return _sort_tokens_list(range_tokens)
    return range_tokens


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


