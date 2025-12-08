import pytest
import os

here = os.path.abspath(os.path.dirname(__file__))

TEST_VOCAB_SIZE = 200
TEST_DIMENSIONS = 20
TEST_BINS = [(1810, 1839), (1840, 1869), (1870, 1899)]


@pytest.fixture()
def mock_corpus(load_test_corpus):
    return load_test_corpus('wordmodels-mock-corpus')
