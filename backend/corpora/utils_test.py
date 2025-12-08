from addcorpus.python_corpora.save_corpus import load_and_save_single_corpus

def corpus_from_api(client, corpus_name: str):
    '''
    Try loading a corpus and fetching it through the API.

    Used for testing that a corpus definition can be used without
    validation/syntax/runtime errors.

    Will take the first corpus returned by the API, so the test data should not contain
    other corpora.
    '''

    load_and_save_single_corpus(corpus_name)

    response = client.get('/api/corpus/')
    assert response.status_code == 200
    assert len(response.data)
    corpus = response.data[0]
    return corpus
