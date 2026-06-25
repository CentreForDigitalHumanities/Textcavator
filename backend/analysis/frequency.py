from typing import List, Dict, Optional

from addcorpus.models import Corpus
from es.client import elasticsearch
from es.search import get_index, total_hits
from analysis.index_utils import token_index_name, token_field_name
from visualization.query import MATCH_ALL, add_filter, make_term_filter

def term_frequency(
    corpus: Corpus,
    metadata_filters: List[Dict],
    term: str,
    field: str,
    multifield: Optional[str] = None,
):
    client = elasticsearch(corpus.name)
    index = token_index_name(get_index(corpus.name))

    if not client.indices.exists(index=index):
        return

    query = term_query(metadata_filters, term, field, multifield)
    results = client.search(
        index=index,
        size=0,
        track_total_hits=True,
        **query,
    )
    return total_hits(results)


def term_query(
    metadata_filters: List[Dict],
    term: str,
    field: str,
    multifield: Optional[str] = None,
):
    query = MATCH_ALL
    for f in metadata_filters:
        query = add_filter(query, f)

    field = token_field_name(field, multifield)
    term_filter = make_term_filter(field, term)
    query = add_filter(query, term_filter)
    return query
