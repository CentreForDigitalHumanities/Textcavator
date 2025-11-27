import { corpusFactory } from '@mock-data/corpus';
import { Corpus, } from './corpus';
import { QueryModel } from './query';
import { SearchFilter } from './field-filter';
import * as _ from 'lodash';
import { Store } from '../store/types';
import { SimpleStore } from '../store/simple-store';

describe('QueryModel', () => {
    let corpus: Corpus;
    let store: Store;
    let query: QueryModel;
    let filter: SearchFilter;
    let filter2: SearchFilter;

    const someDate = new Date('Jan 1 1850');
    const someSelection = ['hooray!'];

    beforeEach(() => {
        corpus = corpusFactory();
        store = new SimpleStore();
        query = new QueryModel(corpus, store);

        filter = query.filterForField(corpus.fields[2]);
        filter2 = query.filterForField(corpus.fields[0]);
    });

    it('should create', () => {
        expect(query).toBeTruthy();
    });

    it('should signal updates', () => {
        let updates = 0;
        query.update.subscribe(() => updates += 1);

        expect(updates).toBe(0);

        query.setQueryText('test');
        expect(updates).toBe(1);

        filter.setToValue(someDate);
        expect(updates).toBe(2);

        filter.deactivate();
        expect(updates).toBe(3);
    });

    it('should not signal irrelevant updates', () => {
        let updates = 0;
        query.update.subscribe(() => updates += 1);

        expect(updates).toBe(0);

        store.paramUpdates$.next({page: '3'});
        expect(updates).toBe(0);
    });

    it('should remove filters', () => {
        let updates = 0;
        query.update.subscribe(() => updates += 1);

        filter.setToValue(someDate);
        filter2.setToValue(someSelection);

        expect(query.activeFilters.length).toBe(2);
        expect(updates).toBe(2);

        filter.setToValue(new Date('Jan 1 1860'));

        expect(query.activeFilters.length).toBe(2);
        expect(updates).toBe(3);

        filter.deactivate();

        expect(query.activeFilters.length).toBe(1);
        expect(updates).toBe(4);

        filter.setToValue(new Date('Jan 1 1870'));

        expect(query.activeFilters.length).toBe(2);
        expect(updates).toBe(5);
    });

    it('should convert to an elasticsearch query', () => {
        expect(query.toEsQuery()).toEqual({
            query: {
                match_all: {}
            }
        });

        query.setQueryText('test');

        expect(query.toEsQuery()).toEqual({
            query: {
                bool: {
                    must: {
                        simple_query_string: {
                            query: 'test',
                            lenient: true,
                            default_operator: 'or',
                        }
                    },
                    filter: []
                }
            }
        });
    });

    it('should formulate parameters', () => {
        expect(query.toQueryParams()).toEqual({});

        query.setQueryText('test');

        expect(query.toQueryParams()).toEqual({
            query: 'test',
        });

        filter.setToValue(someDate);

        expect(query.toQueryParams()).toEqual({
            query: 'test',
            date: '1850-01-01:1850-01-01',
        });

        query.setQueryText('');
        filter.deactivate();

        expect(query.toQueryParams()).toEqual({});
    });

    it('should set from parameters', () => {
        store.paramUpdates$.next({
            query: 'test',
            date: '1850-01-01:1850-01-01',
        });

        const newQuery = new QueryModel(corpus, store);
        expect(newQuery.queryText).toEqual('test');
        expect(newQuery.activeFilters.length).toBe(1);
    });

    it('should formulate a link', () => {
        query.setQueryText('test');
        filter.setToValue(someDate);

        expect(query.toQueryParams()).toEqual({ query: 'test', date: '1850-01-01:1850-01-01' });
    });

    it('should clone', () => {
        query.setQueryText('test');
        filter.setToValue(someDate);

        const clone = query.clone();

        query.setQueryText('different test');
        expect(clone.queryText).toEqual('test');

        filter.setToValue(new Date('Jan 2 1850'));
        expect(query.filterForField(corpus.fields[2]).currentData.min).toEqual(new Date('Jan 2 1850'));
        expect(clone.filterForField(corpus.fields[2]).currentData.min).toEqual(new Date('Jan 1 1850'));
    });
});
