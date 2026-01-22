import * as _ from 'lodash';
import { SimpleStore } from '../store/simple-store';
import { Store } from '../store/types';
import { Corpus } from './corpus';
import { QueryModel } from './query';
import { VisualizationSelector } from './visualization-selector';
import { corpusFactory } from 'mock-data/corpus';

describe('VisualizationSelector', () => {
    let store: Store;
    let corpus: Corpus;
    let query: QueryModel;
    let selector: VisualizationSelector;

    beforeEach(() => {
        store = new SimpleStore();
        corpus = corpusFactory();
        query = new QueryModel(corpus);
    });

    it('should initialise with default values', () => {
        selector = new VisualizationSelector(store, query);
        expect(selector.state$.value).toEqual({
            name: 'resultscount',
            field: corpus.fields[0]
        });
    });

    it('should update the store on init', () => {
        selector = new VisualizationSelector(store, query);
        expect(store.currentParams()).toEqual({
            visualize: 'resultscount',
            visualizedField: 'genre',
        });
    });

    it('should intialise from parameters', () => {
        store.paramUpdates$.next({
            visualize: 'wordcloud',
            visualizedField: 'content'
        });

        selector = new VisualizationSelector(store, query);
        expect(selector.state$.value).toEqual({
            name: 'wordcloud',
            field: corpus.fields[1]
        });
    });

    it('should set the visualisation type', () => {
        selector = new VisualizationSelector(store, query);
        selector.setVisualizationType('termfrequency');
        expect(selector.state$.value).toEqual({
            name: 'termfrequency',
            field: corpus.fields[0]
        });

        selector.setVisualizationType('wordcloud');
        expect(selector.state$.value).toEqual({
            name: 'wordcloud',
            field: corpus.fields[1],
        });
    });

    it('should set the visualisation field', () => {
        selector = new VisualizationSelector(store, query);
        selector.setVisualizedField(corpus.fields[2]);
        expect(selector.state$.value).toEqual({
            name: 'resultscount',
            field: corpus.fields[2],
        });

        selector.setVisualizedField(corpus.fields[1]);
        expect(selector.state$.value).toEqual({
            name: 'wordcloud',
            field: corpus.fields[1],
        });
    });

    it('handles a corpus without visualisations', () => {
        corpus = corpusFactory();
        corpus.fields = [];
        query = new QueryModel(corpus, store);
        selector = new VisualizationSelector(store, query);
        expect(selector.options).toEqual([]);
        expect(selector.state$.value).toBeNull();
    });
});
