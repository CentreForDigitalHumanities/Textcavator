from typing import Optional


def token_index_name(source_index_name: str) -> str:
    return source_index_name + '-tokens'


def token_field_name(field_name: str, multifield: Optional[str] = None,  size: int = 1) -> str:
    return f'{field_name}:{multifield}:{size}' if multifield else f'{field_name}:{size}'

