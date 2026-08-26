import os
import warnings

import pytest
import requests

from addcorpus.python_corpora.corpus import CorpusDefinition
from addcorpus.python_corpora.load_corpus import load_corpus_definition
from corpora.parliament.conftest import CORPUS_TEST_DATA, mock_response_euparl


def corpus_test_name(corpus_spec):
    return corpus_spec['name']


@pytest.mark.parametrize("corpus_object", CORPUS_TEST_DATA, ids=corpus_test_name)
def test_imports(parliament_corpora_settings, monkeypatch, corpus_object):
    monkeypatch.setattr(requests, "get", mock_response_euparl)
    corpus = load_corpus_definition(corpus_object.get('name'))
    assert len(os.listdir(os.path.abspath(corpus.data_directory))) != 0

    start = corpus_object['start'] if 'start' in corpus_object else corpus.min_date
    end = corpus_object['end'] if 'end' in corpus_object else corpus.max_date

    tested_fields = set()
    resulted_fields = set()

    docs = get_documents(corpus, start, end)
    for target in corpus_object.get('docs'):
        doc = next(docs)
        print(doc)
        for key in target:
            tested_fields.add(key)
            assert key in doc
            assert doc[key] == target[key]

        for key in doc:
            resulted_fields.add(key)

    for key in resulted_fields:
        if key not in tested_fields:
            message = 'Key "{}" is included in the result for {} but has no specification'.format(key, corpus_object.get('name'))
            warnings.warn(message)

    docs = get_documents(corpus, start, end)
    assert len(list(docs)) == corpus_object.get('n_documents')


def get_documents(corpus: CorpusDefinition, start, end):
    sources = corpus.sources(
        start=start,
        end=end
    )
    return corpus.documents(sources)
