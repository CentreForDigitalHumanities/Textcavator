from typing import Type

import pytest
from elasticsearch import Elasticsearch

from addcorpus.language_analysis import get_analyzer, LANGUAGES, LanguageAnalyzer
import addcorpus.language_analysis as la
from addcorpus.es_settings import es_settings

def test_get_analyzer():
    assert get_analyzer('nl').code == 'nl'
    assert get_analyzer('nld').code == 'nl'
    assert get_analyzer('nl-BE').code == 'nl'
    assert get_analyzer('nl-Cyrl').code == 'und' # no ignoring script boundaries
    assert get_analyzer('af').code != 'nl' # this match is not close enough


@pytest.mark.parametrize('analyzer_class', LANGUAGES)
def test_language_analyzer_valid(analyzer_class: Type[LanguageAnalyzer]):
    '''
    Check that all analyzers can at least be constructed, and their public
    methods can be called without runtime errors.
    '''

    analyzer = analyzer_class()
    analyzer.code
    analyzer.has_stopwords
    analyzer.has_stemming
    analyzer.char_filters()
    analyzer.token_filters()
    analyzer.analyzers()
    analyzer.standard_analyzer_name
    analyzer.clean_analyzer_name
    analyzer.stemmed_analyzer_name
    analyzer.stopwords()

    if analyzer.has_stopwords:
        assert analyzer.clean_analyzer_name
        assert analyzer.analyzers()[analyzer.clean_analyzer_name]

    if analyzer.has_stemming:
        assert analyzer.stemmed_analyzer_name
        assert analyzer.analyzers()[analyzer.stemmed_analyzer_name]

analyzer_test_cases = [
    {
        'analyzer': la.Dutch,
        'input': 'Ik ben makelaar in koffie, en woon op de Lauriergracht, N° 37.',
        'standard': ['ik', 'ben', 'makelaar', 'in', 'koffie', 'en', 'woon', 'op', 'de', 'lauriergracht', 'n', '37'],
        'clean': ['makelaar', 'koffie', 'woon', 'lauriergracht', 'n'],
        'stemmed': ['makelar', 'koffie', 'won', 'lauriergracht', 'n'],
    },
    {
        'analyzer': la.English,
        'input': 'Shall I compare thee to a summer\'s day?',
        'standard': ['shall', 'i', 'compare', 'thee', 'to', 'a', 'summer', 'day'],
        'clean': ['shall', 'compare', 'thee', 'summer', 'day'],
        'stemmed': ['shall', 'compar', 'thee', 'summer', 'dai'],
    },
    {
        'analyzer': la.French,
        'input': 'Longtemps, je me suis couché de bonne heure.',
        'standard': ['longtemps', 'je', 'me', 'suis', 'couché', 'de', 'bonne', 'heure'],
        'clean': ['longtemps', 'couché', 'bonne', 'heure'],
        'stemmed': ['longtemp', 'couch', 'bone', 'heur'],
    },
    {
        'analyzer': la.German,
        'input': 'Die Welt ist alles, was der Fall ist.',
        'standard': ['die', 'welt', 'ist', 'alles', 'was', 'der', 'fall', 'ist'],
        'clean': ['welt', 'fall'],
        'stemmed': ['welt', 'fall']
    },
    {
        'analyzer': la.Greek,
        'input': 'Μούσα, τραγούδα το θυμό του ξακουστού Αχιλέα, τον έρμο!',
        'standard': ['μουσα', 'τραγουδα', 'το', 'θυμο', 'του', 'ξακουστου', 'αχιλεα', 'τον', 'ερμο'],
        'clean': ['μουσα', 'τραγουδα', 'θυμο', 'ξακουστου', 'αχιλεα', 'ερμο'],
        'stemmed': ['μουσ', 'τραγουδ', 'θυμ', 'ξακουστ', 'αχιλε', 'ερμ'],
    },
    {
        'analyzer': la.Italian,
        'input': 'Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura, ché la diritta via era smarrita.',
        'standard': ['nel', 'mezzo', 'del', 'cammin', 'di', 'nostra', 'vita', 'mi', 'ritrovai', 'per', 'una', 'selva', 'oscura', 'ché', 'la', 'diritta', 'via', 'era', 'smarrita',],
        'clean': ['mezzo', 'cammin', 'vita', 'ritrovai', 'selva', 'oscura', 'ché', 'diritta', 'via', 'smarrita',],
        'stemmed': ['mezzo', 'cammin', 'vita', 'ritrova', 'selva', 'oscur', 'ché', 'diritt', 'via', 'smarrit',],
    },
    {
        'analyzer': la.NorwegianBokmal,
        'input': 'Det var i den Tid, jeg gik omkring og sulted i Kristiania, denne forunderlige By, som ingen forlader, før han har fået Mærker af den.',
        'standard': ['det', 'var', 'i', 'den', 'tid', 'jeg', 'gik', 'omkring', 'og', 'sulted', 'i', 'kristiania', 'denne', 'forunderlige', 'by', 'som', 'ingen', 'forlader', 'før', 'han', 'har', 'fået', 'mærker', 'af', 'den'],
    }
]

def tokens(analyzed_response):
    return [token['token'] for token in analyzed_response['tokens']]

@pytest.mark.parametrize('data', analyzer_test_cases,
    ids=[case['analyzer'].__name__ for case in analyzer_test_cases]
)
def test_language_analyzer_output(es_client: Elasticsearch, test_index_cleanup, data):
    analyzer: LanguageAnalyzer = data['analyzer']()

    index_name = f'test-analyzers-{analyzer.code}'
    settings = es_settings([analyzer.code])
    es_client.indices.create(index=index_name, settings=settings)

    text = data['input']

    def analyzer_output(analyzer_name):
        response = es_client.indices.analyze(
            index=index_name,
            analyzer=analyzer_name,
            text=text,
        )
        return tokens(response.body)

    assert analyzer_output(analyzer.standard_analyzer_name) == data['standard']

    if 'clean' in data:
        assert analyzer_output(analyzer.clean_analyzer_name) == data['clean']

    if 'stemmed' in data:
        assert analyzer_output(analyzer.stemmed_analyzer_name) == data['stemmed']

    es_client.indices.delete(index=index_name)
