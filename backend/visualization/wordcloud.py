from collections import Counter
from typing import Iterable, Dict

from visualization.termvectors import request_termvectors_batched, token_counts
from es import download as download
from es.client import elasticsearch

def make_wordcloud_data(hits: Iterable[Dict], field, corpus_name):
    counts = Counter()

    client = elasticsearch(corpus_name)
    docs = request_termvectors_batched(hits, client, False, [field])
    for _, doc in docs:
        counts.update(token_counts(doc, field))

    output = [{'key': word, 'doc_count': freq} for word, freq in counts.items()]
    return output

