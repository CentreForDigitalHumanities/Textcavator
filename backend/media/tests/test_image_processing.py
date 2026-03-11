import pytest
from media.image_processing import pdf_pages


@pytest.mark.parametrize('n_pages,index,window,expected', [
    pytest.param(10, 5, 2, [3, 4, 5, 6, 7], id="middle"),
    pytest.param(10, 0, 2, [0, 1, 2], id="start"),
    pytest.param(10, 9, 2, [7, 8, 9], id="end"),
])
def test_pdf_pages(n_pages, index, window, expected):
    assert pdf_pages(index, n_pages, window) == expected
