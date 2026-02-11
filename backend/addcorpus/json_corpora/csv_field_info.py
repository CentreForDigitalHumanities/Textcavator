import datetime
import os
from typing import Callable, Dict, Union, List, Tuple
import csv

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


def get_csv_info(path: Union[str, os.PathLike], **kwargs) -> Dict:
    '''Get information about a CSV file'''
    encoding = kwargs.get('encoding', 'utf-8')
    # sniff out CSV dialect to find delimiter
    with open(path, 'r', encoding=encoding) as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
    columns, data = _read_csv(path, dialect.delimiter)
    info = {
        'n_rows': len(data),
        'fields': [
            {
                'name': col_name,
                'type': map_col(_get_col_values(col_name, data)),
            }
            for col_name in columns
        ],
        'delimiter': dialect.delimiter,
    }
    return info


def _read_csv(
    path: Union[str, os.PathLike], delimiter: str
) -> Tuple[List[str], List[Dict[str, str]]]:
    '''
    Read CSV contents, but stop after lines exceeds `limit`.
    '''
    with open(path) as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        return reader.fieldnames, [row for row in reader]


def _get_col_values(col: str, data: List[Dict[str, str]]) -> List[str]:
    return [row[col] for row in data]


def map_col(col: List[Dict[str, str]]) -> str:
    if _is_int_col(col):
        return 'integer'
    if _is_float_col(col):
        return 'float'
    if _is_bool_col(col):
        return 'boolean'
    if _is_url_col(col):
        return 'url'
    if _is_date_col(col):
        return 'date'
    if _is_long_text_col(col):
        return 'text_content'
    return 'text_metadata'


def _is_int_col(col: List[str]) -> bool:
    return _col_is_null_or_type(col, _is_int)


def _is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except:
        return False


def _is_float_col(col: List[str]) -> bool:
    return _col_is_null_or_type(col, _is_float)


def _is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except:
        return False


def _is_bool_col(col: List[str]) -> bool:
    return _col_is_null_or_type(col, _is_bool)


def _is_bool(value: str) -> bool:
    return value.lower() in ['true', 'false']


def _is_date_col(col: List[str]) -> bool:
    return _col_is_null_or_type(col, _is_date)


def _is_date(value: str) -> bool:
    try:
        datetime.datetime.strptime(value, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


def _is_url_col(col: List[str]) -> bool:
    return _col_is_null_or_type(col, _is_url)


def _is_url(value: str) -> bool:
    validator = URLValidator()
    try:
        validator(value)
        return True
    except ValidationError:
        return False

def _col_is_null_or_type(col: List[str], is_type: Callable[[str], bool]) -> bool:
    '''Check if a column only contains the desired type or missing values.
    '''
    is_not_null_and_type = lambda value: value and is_type(value)
    is_null_or_type = lambda value: not value or is_type(value)
    return any(map(is_not_null_and_type, col)) and all(map(is_null_or_type, col))


def _is_long_text_col(col: List[str]) -> bool:
    return any(map(_is_long_text, col))


def _is_long_text(value: str) -> bool:
    return value and (len(value) > 100 or '\n' in value)
