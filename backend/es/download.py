from typing import Dict, Tuple

from es.client import elasticsearch, server_for_corpus
from es.search import get_index, search, hits, total_hits
import itertools
from django.conf import settings

def scroll(corpus: str, query_model, download_size=None, client=None, **kwargs) -> Tuple[itertools.chain[Dict], int]:
    chunks, total = scroll_chunks(corpus, query_model,
                                  download_size, client, **kwargs)
    output = itertools.chain(*chunks)
    return output, total


def scroll_chunks(corpus: str, query_model, download_size=None, client=None, **kwargs):
    index = get_index(corpus)
    if not client:
        client = elasticsearch(index)
    server_conf = settings.SERVERS.get(server_for_corpus(corpus))
    scroll_timeout = server_conf['scroll_timeout']
    scroll_page_size = server_conf['scroll_page_size']
    size = min(download_size,
               scroll_page_size) if download_size else scroll_page_size
    total = get_total_hits(client, index, query_model, **kwargs)
    chunks = make_chunks(client, index, size,
                         scroll_timeout, query_model, total, download_size, **kwargs)
    return chunks, total


def get_total_hits(client, index, query_model, **kwargs) -> int:
    search_results = client.search(
        index=index,
        size=0,
        track_total_hits=True,
        **query_model,
        **kwargs
    )
    return total_hits(search_results)


def make_chunks(client, index, size, scroll_timeout, query_model, total, download_size=None, **kwargs):
    search_results = client.search(
        index=index,
        size=size,
        scroll=scroll_timeout,
        timeout='60s',
        **query_model,
        **kwargs
    )
    yield hits(search_results)

    if not download_size or download_size > total:
        download_size = total
    num_results = len(hits(search_results))
    scroll_id = search_results['_scroll_id']
    while num_results < download_size:
        search_results = client.scroll(scroll_id=scroll_id,
                                       scroll=scroll_timeout)
        scroll_id = search_results['_scroll_id']
        num_results += len(hits(search_results))
        yield hits(search_results)
    client.clear_scroll(scroll_id=scroll_id)


def normal_search(corpus, query_model):
    result = search(
        corpus=corpus,
        query_model=query_model
    )
    return hits(result)
