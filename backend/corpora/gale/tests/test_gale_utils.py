import os
import pytest
from corpora.gale.gale import when_not_empty, fix_path_sep, clean_date

def test_when_not_empty():
    def uppercase(s: str) -> str:
        return s.upper()

    transform = when_not_empty(uppercase)

    with pytest.raises(Exception):
        uppercase(None)

    assert transform('foo') == 'FOO'
    assert transform(None) == None


@pytest.fixture()
def posix_os():
    if not os.name == 'posix':
        pytest.skip()

def test_fix_path_sep(posix_os):
    assert fix_path_sep('data\\images\\0001.jpg') == 'data/images/0001.jpg'

@pytest.mark.parametrize('value,expected', [
    ('Date Unknown', None),
    ('February 1, 1890', '1890-02-01'),
    ('February 1,1890', '1890-02-01'),
    ('February 1st 1890-February 7th 1890', '1890-02-01'),
])
def test_clean_date(value, expected):
    assert clean_date(value) == expected
