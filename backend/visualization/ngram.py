from collections import Counter
from typing import Tuple, Dict, List, Literal, Iterable, Optional
from elasticsearch import Elasticsearch
from itertools import chain
from math import log2, prod

from addcorpus.models import CorpusConfiguration
from datetime import datetime
from es.download import scroll, search
from es.client import elasticsearch
from visualization import query, termvectors


def get_ngrams(results, number_of_ngrams=10, method='absolute'):
    """Given a query and a corpus, get the words that occurred most frequently around the query term"""
    ngrams = get_top_n_ngrams(results, number_of_ngrams, method=method)

    return {
        'words': ngrams,
        'time_points': [result['time_interval'] for result in results]
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

def get_total_term_count(corpus_name: str, es_query: Dict, field: str) -> int:
    agg_query = {
        **es_query,
        'size': 0,
        'aggs': {'word_count': {'sum': {'field': f'{field}.length'}}}
    }
    result = search(corpus_name, agg_query)
    value = result.body['aggregations']['word_count']['value']
    return int(value)


def tokens_by_time_interval(
    corpus_name: str,
    es_query: Dict,
    field: str,
    bin: Tuple[int, int],
    ngram_size: int,
    term_position: str,
    collect_ttf: Optional[bool],
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
    docs = termvectors.request_termvectors_batched(
        search_results, client, collect_ttf, [field]
    )
    for _, vectors in docs:
        tokens, ttfs = _count_tokens_in_document(
            vectors, client, field, query_text,
            term_positions, ngram_size,
            collect_ttf=collect_ttf,
            mode=mode,
        )
        bin_ngrams.update(tokens)
        ngram_ttfs.update(ttfs)

    results = {
        'time_interval': format_time_label(bin[0], bin[1]),
        'ngrams': bin_ngrams
    }
    if collect_ttf:
        total_term_count = get_total_term_count(corpus_name, es_query, field)
        results['total_term_count'] = total_term_count
        results['ngram_ttfs'] = ngram_ttfs
    return results


def _count_tokens_in_document(
    termvector_result: Dict,
    client: Elasticsearch,
    field: str,
    query_text: str,
    term_positions: List[int],
    ngram_size: int,
    collect_ttf: bool = False,
    mode: Literal['ngrams', 'collocates'] = 'ngrams',
) -> Tuple[Counter, Dict]:
    '''
    Count token frequencies surrounding the search term from a document
    '''
    tokens = Counter()
    ttfs = dict()
    # get the term vectors for the hit
    terms = termvectors.get_terms(termvector_result, field)
    if terms:
        sorted_tokens = termvectors.get_tokens(terms, sort=True)
        matches = termvectors.token_matches(sorted_tokens, query_text, termvector_result['_index'], field, client)
        token_ranges = _token_ranges(
            matches, term_positions, ngram_size, len(sorted_tokens), mode=mode
        )
        for start, stop in token_ranges:
            ngram = sorted_tokens[start:stop]
            words = ' '.join([token['term'] for token in ngram])
            if collect_ttf:
                ttfs[words] = [token['ttf'] for token in ngram]
            tokens.update({ words: 1})
    return tokens, ttfs


def _token_ranges(
    matches: Iterable[Tuple[int, int, str]],
    term_positions: List[int],
    ngram_size: int,
    document_size: int,
    mode: Literal['ngrams', 'collocates'] = 'ngrams',
) -> Iterable[Tuple[int, int]]:
    '''
    Provides ranges for every token  (n-gram or collocate) surrounding the search term.
    '''
    for match_start, match_stop, _match_content in matches:
        if mode == 'ngrams':
            ranges = _ngram_token_ranges(match_start, match_stop, term_positions, ngram_size)
        else:
            window_size = ngram_size - 1
            ranges = _collocate_token_ranges(match_start, match_stop, window_size)

        for start, stop in ranges:
            if start >= 0 and stop <= document_size:
                yield start, stop


def _ngram_token_ranges(
    match_start: int, match_stop: int,
    term_positions: List[int],
    ngram_size: int,
) -> Iterable[Tuple[int, int]]:
    '''
    From the range of a token match, generates ranges for n-grams containing the token.
    '''
    for i in term_positions:
        start = match_start - i
        stop = match_stop - 1 - i + ngram_size
        yield start, stop


def _collocate_token_ranges(
    match_start: int, match_stop: int,
    window_size: int,
) -> Iterable[Tuple[int, int]]:
    '''
    From the range of a token match, generates ranges for collocates surrounding the
    token.
    '''

    window_start = match_start - window_size
    window_stop = match_stop + window_size
    window = chain(range(window_start, match_start), range(match_stop, window_stop))

    for i in window:
        yield i, i + 1



def _absolute_frequency(
    ngram_count: int, term_counts: List[int], total_word_count: int
) -> float:
    return ngram_count

def _legacy_compensated_frequency(
    ngram_count: int, term_counts: List[int], total_word_count: int
) -> float:
    norm = (sum(term_counts) / len(term_counts))
    return ngram_count / norm

def _pmi(
    ngram_count: int, term_counts: List[int], total_word_count: int
) -> float:
    relative_frequency = ngram_count / total_word_count
    norm = prod([
        count / total_word_count
        for count in term_counts
    ])
    return log2(relative_frequency / norm)


def _ngram_frequency(
    ngram: str,
    ngram_counts: Counter,
    ttfs: Optional[Dict],
    total_word_count: int,
    method='absolute',
) -> float | int:
    methods = {
        'absolute': _absolute_frequency,
        'legacy': _legacy_compensated_frequency,
        'pmi': _pmi
    }
    func = methods[method]
    count = ngram_counts.get(ngram, 0)
    if not count:
        return 0
    if method in ['legacy', 'pmi']:
        if not ttfs:
            raise ValueError(f'ttfs dict is required for frequency method {method}')
        term_counts = ttfs.get(ngram)
    else:
        term_counts = None

    return func(count, term_counts, total_word_count)


def _select_top_ngrams(
    counter: Counter, ttfs: Dict, total_word_count: int, method='absolute', n=10
) -> List[str]:
    if method == 'absolute':
        return [ngram for ngram, _count in counter.most_common(n)]
    else:
        frequency = lambda ngram: _ngram_frequency(ngram, counter, ttfs, total_word_count, method)
        sorted_ngrams = sorted(counter.keys(), reverse=True, key=frequency)
        return [ngram for ngram, _ in zip(sorted_ngrams, range(n))]


def get_top_n_ngrams(results, number_of_ngrams=10, method='absolute'):
    """
    Converts a list of documents with tokens into n dataseries, listing the
    frequency of the top n tokens and their frequency in each document.

    Input:
    - `results`: a list of dictionaries with the following keys:
        - `'ngram'`: Counter objects with ngram frequencies
        - `'time_interval'`: the time intervals for which the ngrams were counted
        - `'ngram_ttfs'` (optional): total term frequencies per term
        - `total_term_count`: total words in the dataset
    - `number_of_ngrams`: the number of top ngrams to return
    - `method`: frequency method to use (absolute/legacy/pmi)

    Output:
    A list of number_of_ngrams data series. Each series is a dict with two keys: `'label'` contains the content of a token (presumably an
    ngram string), `'data'` contains a list of the frequency of that token in each document. Depending on `divide_by_ttf`,
    this is absolute or relative to the total term frequencies provided.
    """
    total_counter = Counter()
    total_frequencies = dict()
    total_term_count = None
    for result in results:
        total_counter.update(result['ngrams'])
        total_frequencies.update(result.get('ngram_ttfs', {}))
        total_term_count = result.get('total_term_count')

    top = _select_top_ngrams(
        total_counter, total_frequencies, total_term_count,
        method=method, n=number_of_ngrams,
    )

    sorted_results = sorted(results, key=lambda r: r['time_interval'])
    output = [
        {
            'label': ngram,
            'data': [
                _ngram_frequency(
                    ngram,
                    interval['ngrams'],
                    interval.get('ngram_ttfs'),
                    interval.get('total_term_count'),
                    method,
                )
                for interval in sorted_results
            ]
        }
        for ngram in top
    ]

    return output
