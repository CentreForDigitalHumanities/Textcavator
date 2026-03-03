from collections import Counter
from typing import Iterable, Dict

from addcorpus.models import CorpusConfiguration, Field
from visualization.termvectors import request_termvectors_batched, term_counts
from es import download as download
from es.client import elasticsearch

def _wordcloud_search_field(corpus_name: str, field_name: str) -> bool:
    corpus_config = CorpusConfiguration.objects.get(corpus__name=corpus_name)
    field: Field = corpus_config.fields.get(name=field_name)
    has_clean_field = 'clean' in field.es_mapping.get('fields', {})
    if has_clean_field:
        return field_name + '.clean'
    return field_name


def make_wordcloud_data(hits: Iterable[Dict], field_name, corpus_name):
    search_field = _wordcloud_search_field(corpus_name, field_name)

    counts = Counter()
    client = elasticsearch(corpus_name)
    docs = request_termvectors_batched(hits, client, False, [search_field])
    for _, doc in docs:
        counts.update(term_counts(doc, search_field))

    output = [{'key': word, 'doc_count': freq} for word, freq in counts.items()]
    return output

