import pytest

from es.versioning import highest_version_in_result, version_from_name

@pytest.mark.parametrize(
    'name,version',
    [
        ('foo-1', 1),
        ('foo-11', 11),
        ('foo', None),
        ('foo-bar-3', None),
        ('foo-1-or-something', None),
    ]
)
def test_version_from_name(name, version):
    assert version_from_name(name, 'foo') == version


@pytest.mark.parametrize(
    'indices,version',
    [
        (['test-versioning-1', 'test-versioning-2'], 2),
        (['test-versioning-5'], 5),
        ([], 0),
    ]
)
def test_highest_version_number(indices, version):
    base_name = 'test-versioning'

    assert highest_version_in_result(indices, base_name) == version
