from corpora_test.basic.mock_csv_corpus import ExampleCorpus
import os

here = os.path.abspath(os.path.dirname(__file__))


target_documents = [
    {
        'character': 'HAMLET',
        'line': "Whither wilt thou lead me? Speak, I\'ll go no further."
    },
    {
        'character': 'GHOST',
        'line': "Mark me."
    },
    {
        'character': 'HAMLET',
        'line': "I will."
    },
    {
        'character': 'GHOST',
        'line': "My hour is almost come,",
    },
    {
        'character': 'GHOST',
        'line': "When I to sulph\'rous and tormenting flames",
    },
    {
        'character': 'GHOST',
        'line': "Must render up myself.",
    },
    {
        'character': 'HAMLET',
        'line': "Alas, poor ghost!",
    },
    {
        'character': 'GHOST',
        'line': "Pity me not, but lend thy serious hearing",
    },
    {
        'character': 'GHOST',
        'line': "To what I shall unfold.",
    },
    {
        'character': 'HAMLET',
        'line': "Speak, I am bound to hear."
    },
]


def test_csv():
    corpus = ExampleCorpus()

    sources = list(corpus.sources(start=corpus.min_date, end=corpus.max_date))
    assert len(sources) == 1 and sources[0][1] == {'filename': 'example.csv'}

    docs = corpus.source2dicts(sources[0])
    for doc, target in zip(docs, target_documents):
        assert doc == target
