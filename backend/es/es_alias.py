from typing import Generator, List

from addcorpus.models import CorpusConfiguration
from es.client import client_from_config
from es.models import Server, Index
from es.versioning import has_base_name

def get_current_index_names(corpus: CorpusConfiguration, client) -> List[str]:
    """get the names of the current corpus' associated index"""
    return list(client.indices.get(index=corpus.es_index).keys())


def indices_with_alias(server: Server, alias: str, base_name=None) -> Generator[Index, None, None]:
    '''
    Filter indices with an alias.

    Add `base_name` to only select indices with this base name.
    '''
    client = client_from_config(server.configuration)
    if client.indices.exists_alias(name=alias):
        for index_name in client.indices.get_alias(name=alias):
            if (not base_name) or has_base_name(index_name, base_name):
                aliased_index, _ = Index.objects.get_or_create(
                    server=server,
                    name=index_name,
                )
                yield aliased_index
