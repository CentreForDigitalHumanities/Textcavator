'''
Utilities for Simple Query String syntax
'''

from typing import List, Tuple, Optional, Union
import re

def collect_terms(query_text: str) -> List[str]:
    '''
    Return all terms in a simple query string.

    Splits a query into terms, which may be either phrase terms or single terms. Operators
    are not included.

    Returns a list of strings, each of which is a single term. These still include
    decorators like fuzzy search, negation, or quotation marks for phrase terms. Order
    may not match the query.
    '''

    if '(' in query_text and ')' in query_text:
        opening = re.compile(r'\(')
        closing = re.compile(r'\)')
        in_group, outside_group = _extract_group(query_text, opening, closing, False)
        if in_group:
            return collect_terms(in_group) + collect_terms(outside_group)

    if '"' in query_text:
        opening = re.compile(r'-?"')
        closing = re.compile(r'"(~\d+)?')
        in_qoutes, outside_qoutes = _extract_group(query_text, opening, closing, True)
        if in_qoutes:
            return [in_qoutes] + collect_terms(outside_qoutes)

    terms = list(filter(_is_term, query_text.split()))
    return terms


def _is_term(query_part: str) -> bool:
    '''
    Whether a query section is a term (and not an operator)
    '''
    return query_part not in ['+', '|']


def _extract_group(
    query_text: str, opening: re.Pattern, closing: re.Pattern, keep_bounds: bool,
) -> Tuple[Optional[str], str]:
    '''
    Split a group from the rest of the query. Used to extract sections in parentheses
    or quotes.

    Parameters:
        query_text: query text
        opening: opening pattern
        closing: closing pattern
        keep_bounds: whether to include the opening/closing characters or strip them

    Returns:
        A tuple with the extracted group (`None` if there is none), and the query
        with the group removed. If `keep_bounds` is true, the extracted group will
        include the opening/closing characters.
    '''

    bounds = _find_group(query_text, opening, closing)

    if bounds:
        opening_start, opening_end, closing_start, closing_end = bounds
        if keep_bounds:
            in_group = query_text[opening_start : closing_end]
        else:
            in_group = query_text[opening_end : closing_start]
        outside_group = query_text[:opening_start] + query_text[closing_end:]
        return in_group, outside_group

    return (None, query_text)


def _find_group(
    query_text: str, opening: re.Pattern, closing: re.Pattern,
) -> Optional[Tuple[int, int, int, int]]:
    '''
    Find the opening/closing indices for a group. Will respect nesting if opening and
    closing patterns do not overlap.

    Returns:
        Tuple with indices of the start of the opening substring, end of the opening
            substring, start of the closing substring, end of the closing substring.
    '''
    opening_match = re.search(opening, query_text)

    if not opening_match:
        return

    nesting = 0
    for i in range(opening_match.end(), len(query_text)):
        substring = query_text[i:]
        if closing_match := re.match(closing, substring):
            if not nesting:
                return opening_match.start(), opening_match.end(), \
                    i, i + closing_match.end()
            else:
                nesting -= 1
        elif re.match(opening, substring):
            nesting += 1



def is_prefix(term: str) -> bool:
    return term.endswith('*')

def is_negated(term: str) -> bool:
    return term.startswith('-')
