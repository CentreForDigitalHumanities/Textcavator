from typing import Optional


def bow_index_name(source_index_name: str) -> str:
    return source_index_name + '.bow'

def content_field_name(name: str, multifield: Optional[str] = None):
    return f'{name}.{multifield}' if multifield else name
