'''
Utility functions for parsing and generating versioned index names.
'''

import re
from typing import Optional, List
from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch

def indices_with_base_name(client: Elasticsearch, base_name: str) -> List[str]:
    pattern = base_name + '*'
    if not client.indices.exists(index=pattern, allow_no_indices=False):
        return []

    res = client.indices.get(index=pattern, allow_no_indices=False)
    return [
        index_name for index_name in res.keys()
        if has_base_name(index_name, base_name)
    ]


def next_version_number(client: Elasticsearch, base_name: str) -> int:
    '''
    Get version number for a new versioned index (e.g. `indexname-1`).

    Will be 1 if the base name does not match any existing indices (either as the index
    name or an alias).

    If the name matches existing indices, this will use the highest version number to
    determine the next version.

    Parameters
        client -- ES client
        base_name -- The unversioned name
    '''

    response = indices_with_base_name(client, base_name)
    if not response:
        return 1

    highest_version = highest_version_in_result(response, base_name)
    return highest_version + 1


def has_base_name(index_name: str, base_name: str) -> bool:
    return bool(re.match(rf'{base_name}(-[0-9]+)?$', index_name))


def version_from_name(index_name: str, base_name: str) -> Optional[int]:
    '''
    Helper function to extract version number from an index name.

    Format of the index name should be `{base_name}-{version}`, e.g. `foo-5`.

    If the name does not match this pattern, e.g. `foo`, `foo-bar-5`, `foo-5.3`,
    `bar`, etc., this function will return `None`.
    '''

    match = re.match('{}-([0-9]+)$'.format(base_name), index_name)
    if match:
        return int(match.group(1))


def highest_version_in_result(index_names: List[str], base_name: str) -> int:
    '''
    Extract the highest version number from the Elasticsearch response to an indices
    query.

    This assumes that versioned index names follow the pattern `{base_name}-{version}`,
    e.g. `mycorpus-3`. If an index doesn't match this pattern, it will be ignored.

    If the results do not contain any (versioned) indices, this will return 0.

    Parameters:
        indices -- the API response from Elasticsearch (not a list of names!), e.g. from
            `client.indices.get` or `client.indices.get_alias`.
        base_name -- The unversioned name currently being updated. This will be used to
            exclude indices starting with different names under the same alias.
    '''
    versions = [
        version_from_name(index_name, base_name) for index_name in index_names
    ]

    try:
        return max([v for v in versions if v is not None])
    except:
        return 0
