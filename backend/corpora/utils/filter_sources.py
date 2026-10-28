from datetime import datetime, date

from addcorpus.python_corpora.corpus import CorpusDefinition

def normalize_date(value: datetime | date | int, round='up') -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, int):
        if round == 'up':
            return date(value, 12, 31)
        else:
            return date(value, 1, 1)


def in_date_range(corpus: CorpusDefinition, start: datetime | date, end: datetime | date) -> bool:
    start_date = start or corpus.min_date
    end_date = end or corpus.max_date

    return normalize_date(start_date, 'down') <= normalize_date(corpus.max_date, 'up') \
        and normalize_date(end_date, 'up') >= normalize_date(corpus.min_date, 'down')
