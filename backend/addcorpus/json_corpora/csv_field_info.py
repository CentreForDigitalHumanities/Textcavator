import datetime
import os
from typing import Callable, Dict, Optional, Union, Any
import csv

import numpy as np
import pandas as pd

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


def get_csv_info(path: Union[str, os.PathLike], **kwargs) -> Dict:
    '''Get information about a CSV file'''
    encoding = kwargs.get('encoding', 'utf-8')
    # sniff out CSV dialect to find delimiter
    with open(path, 'r', encoding=encoding) as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
    df = pd.read_csv(path, encoding=encoding, sep=dialect.delimiter, **kwargs)
    info = {
        'n_rows': len(df),
        'fields': [
            {'name': col_name, 'type': map_col(df[col_name])} for col_name in df.columns],
        'delimiter': dialect.delimiter,
    }
    return info


def map_col(col: pd.Series) -> str:
    if col.dtypes == object:
        if is_url_col(col):
            return 'url'
        if is_date_col(col):
            return 'date'
        if is_long_text_col(col):
            return 'text_content'
        return 'text_metadata'
    elif col.dtypes == np.float64:
        return 'float'
    elif col.dtypes == np.int64:
        return 'integer'
    elif col.dtypes == bool:
        return 'boolean'
    return 'text'


def is_date_col(col: pd.Series) -> bool:
    '''Check if a column only contains dates or missing values
    Converts empty strings to None because they are non picked up by `isna()`
    '''
    non_null = col.replace('', None)
    non_null = non_null[~non_null.isna()]
    if non_null.empty:
        return False
    mask = non_null.transform(is_date)
    return mask.all()



def col_is_null_or_type(col: pd.Series, coltype: Callable[[Any], bool]) -> bool:
    '''Check if a column only contains the desired type or missing values.
    Converts empty strings to None because they are not picked up by `isna()`
    '''
    non_null = col.replace('', None)
    non_null = non_null[~non_null.isna()]
    if non_null.empty:
        return False
    mask = non_null.transform(coltype)
    return mask.all()


def is_url_col(col: pd.Series) -> bool:
    return col_is_null_or_type(col, is_url)


def is_date(input: str) -> Optional[datetime.datetime]:
    try:
        datetime.datetime.strptime(input, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


def is_url(input: str) -> bool:
    validator = URLValidator()
    try:
        validator(input)
        return True
    except ValidationError:
        return False


def is_long_text(value: Any) -> bool:
    return isinstance(value, str) and (len(value) > 100 or '\n' in value)


def is_long_text_col(col: pd.Series) -> bool:
    return col.apply(is_long_text).any()
