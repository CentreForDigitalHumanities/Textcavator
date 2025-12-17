from collections import Counter
from typing import Tuple, Dict, List, Literal
from elasticsearch import Elasticsearch

from addcorpus.models import CorpusConfiguration
from datetime import datetime
from es.download import scroll
from es.client import elasticsearch
from visualization import query, termvectors


def get_ngrams(results, number_of_ngrams=10):
    """Given a query and a corpus, get the words that occurred most frequently around the query term"""
    ngrams = []
    ngrams = get_top_n_ngrams(results, number_of_ngrams)

    return {
        'words': ngrams,
        'time_points': sorted([result['time_interval'] for result in results])
    }


def format_time_label(start_year, end_year):
    if start_year == end_year:
        return str(start_year)
    else:
        return '{}-{}'.format(start_year, end_year)

def get_total_time_interval(es_query, corpus) -> Tuple[datetime, datetime]:
    """
    Min and max date for the search query and corpus. Returns the dates from the query if provided,
    otherwise the min and max date from the corpus configuration.
    """

    query_min, query_max = query.get_date_range(es_query)

    if query_min and query_max:
        return query_min, query_max

    corpus_conf = CorpusConfiguration.objects.get(corpus__name=corpus)
    corpus_min = datetime(corpus_conf.min_year, month=1, day=1)
    corpus_max = datetime(corpus_conf.max_year, month=12, day=31)

    min_date = query_min if query_min and query_min > corpus_min else corpus_min
    max_date = query_max if query_max and query_max < corpus_max else corpus_max

    return min_date, max_date


def get_time_bins(es_query, corpus):
    """Wide bins for a query. Depending on the total time range of the query, time intervervals are
    10 years (>100 yrs), 5 years (100-20 yrs) of 1 year (<20 yrs)."""

    min_date, max_date = get_total_time_interval(es_query, corpus)
    min_year, max_year = min_date.year, max_date.year
    time_range = max_year - min_year

    if time_range < 1:
        year_step = None
    elif time_range <= 20:
        year_step = 1
    elif time_range <= 100:
        year_step = 5
    else:
        year_step = 10

    if year_step:
        bins = [(start, min(max_year, start + year_step - 1)) for start in range(min_year, max_year, year_step)]
        bins_max = bins[-1][1]

        if bins_max < max_year:
            bins.append((bins_max + 1, max_year))

    else:
        bins = [(min_year, max_year)]

    return bins


def tokens_by_time_interval(
    corpus_name: str,
    es_query: Dict,
    field: str,
    bin: Tuple[int, int],
    ngram_size: int,
    term_position: str,
    freq_compensation: bool | None,
    subfield: str,
    max_size_per_interval: int,
    date_field: str,
    mode: Literal['ngrams', 'collocates'] = 'ngrams',
    **kwargs
) -> Dict:
    client = elasticsearch(corpus_name)
    positions_dict = {
        'any': list(range(ngram_size)),
        'first': [0],
        'second': [1],
        'third': [2],
        'fourth': [3],
    }
    term_positions = positions_dict[term_position]
    ngram_ttfs = dict()

    query_text = query.get_query_text(es_query)
    field = field if subfield == 'none' else '.'.join([field, subfield])

    start_date = datetime(bin[0], 1, 1)
    end_date = datetime(bin[1], 12, 31)

    # filter query on this time bin
    date_filter = query.make_date_filter(start_date, end_date, date_field)
    narrow_query = query.add_filter(es_query, date_filter)
    #search for the query text
    search_results, _total = scroll(
        corpus=corpus_name,
        query_model=narrow_query,
        client=client,
        download_size=max_size_per_interval,
    )
    bin_ngrams = Counter()
    for hit in search_results:
        tokens, ttfs = _count_tokens_in_document(
            hit, client, field, query_text,
            term_positions, ngram_size,
            freq_compensation=freq_compensation,
            mode=mode,
        )
        bin_ngrams.update(tokens)
        ngram_ttfs.update(ttfs)

    results = {
        'time_interval': format_time_label(bin[0], bin[1]),
        'ngrams': bin_ngrams
    }
    if freq_compensation:
        results['ngram_ttfs'] = ngram_ttfs
    return results


def _count_tokens_in_document(
    hit: Dict,
    client: Elasticsearch,
    field: str,
    query_text: str,
    term_positions: List[int],
    ngram_size: int,
    freq_compensation: bool | None = None,
    mode: Literal['ngrams', 'collocates'] = 'ngrams',
) -> Tuple[Counter, Dict]:
    '''
    Count token frequencies surrounding the search term from a document
    '''
    tokens = Counter()
    ttfs = dict()
    # get the term vectors for the hit
    result = client.termvectors(
        index=hit['_index'],
        id=hit['_id'],
        term_statistics=freq_compensation,
        fields=[field]
    )
    terms = termvectors.get_terms(result, field)
    if terms:
        sorted_tokens = termvectors.get_tokens(terms, sort=True)
        for match_start, match_stop, match_content in termvectors.token_matches(sorted_tokens, query_text, hit['_index'], field, client):
            for j in term_positions:
                start = match_start - j
                stop = match_stop - 1 - j + ngram_size
                if start >= 0 and stop <= len(sorted_tokens):
                    ngram = sorted_tokens[start:stop]
                    words = ' '.join([token['term'] for token in ngram])
                    if freq_compensation:
                        ttf = sum(token['ttf'] for token in ngram) / len(ngram)
                        ttfs[words] = ttf
                    tokens.update({ words: 1})
    return tokens, ttfs


def get_top_n_ngrams(results, number_of_ngrams=10):
    """
    Converts a list of documents with tokens into n dataseries, listing the
    frequency of the top n tokens and their frequency in each document.

    Input:
    - `results`: a list of dictionaries with the following fields:
    'ngram': Counter objects with ngram frequencies
    'time_interval': the time intervals for which the ngrams were counted
    (optional): 'ngram-ttf': averaged total term frequencies - only computed if freq_compensation was requested
    - `number_of_ngrams`: the number of top ngrams to return

    Output:
    A list of number_of_ngrams data series. Each series is a dict with two keys: `'label'` contains the content of a token (presumably an
    ngram string), `'data'` contains a list of the frequency of that token in each document. Depending on `divide_by_ttf`,
    this is absolute or relative to the total term frequencies provided.
    """
    total_counter = Counter()
    for result in results:
        total_counter.update(result['ngrams'])
    sorted_results = sorted(results, key=lambda r: r['time_interval'])

    number_of_results = min(number_of_ngrams, len(total_counter))

    if 'ngram_ttfs' in results[0]:
        total_frequencies = {}
        for result in results:
            total_frequencies.update(result['ngram_ttfs'])
        def frequency(ngram, counter): return counter.get(ngram, 0.0) / max(1.0, total_frequencies[ngram])
        def overall_frequency(ngram): return frequency(ngram, total_counter)
        top_ngrams = sorted(total_counter.keys(), key=overall_frequency, reverse=True)[:number_of_results]
    else:
        def frequency(ngram, counter): return counter.get(ngram, 0)
        top_ngrams = [word for word, freq in total_counter.most_common(number_of_results)]
    output = [{
            'label': ngram,
            'data': [frequency(ngram, result['ngrams'])
                for result in sorted_results]
        }
        for ngram in top_ngrams]

    return output
