import {
    highlightFromParams, omitNullParameters, pageFromParams, pageToParams, searchFieldsFromParams,
    sortSettingsFromParams, sortSettingsToParams
} from './params';
import { corpusFactory } from '@mock-data/corpus';
import { Corpus, CorpusField, SortState } from '@models';
import * as _ from 'lodash';
import { PageParameters, PageResultsParameters } from '@models/page-results';

describe('searchFieldsFromParams', () => {
    it('should parse field parameters', () => {
        const params = {fields: 'content'};
        const corpus = corpusFactory();
        const fields = searchFieldsFromParams(params, corpus);
        expect(fields.map(f => f.name)).toEqual(['content']);
    });

    it('should include stemmed multifields', () => {
        const corpus = corpusFactory();
        const fields = searchFieldsFromParams(
            { fields: 'content,content.stemmed' },
            corpus
        );
        expect(fields.map(f => f.name)).toEqual(['content', 'content.stemmed']);
    })
});

describe('highlightFromParams', () => {
    it('should parse highlight parameters', () => {
        const params = {highlight: '100'};
        const highlight = highlightFromParams(params);
        expect(highlight).toBe(100);
    });

    it('should parse empty parameters', () => {
        const highlight = highlightFromParams({});
        expect(highlight).toBe(undefined);
    });
});

describe('sortSettingsFromParams', () => {
    let corpus: Corpus;
    let sortField: CorpusField;

    beforeEach(() => {
        corpus = corpusFactory();
        sortField = corpus.fields[2]
    })

    it('should parse the default state', () => {
        const empty = {};

        expect(sortSettingsFromParams(empty, corpus)).toEqual([undefined, 'desc']);

        corpus.defaultSort = [sortField, 'desc'];
        expect(sortSettingsFromParams(empty, corpus)).toEqual([sortField, 'desc']);
    });

    it('should be the inverse of sortSettingsToParams', () => {
        const sort: SortState = [sortField, 'asc'];
        const params = sortSettingsToParams(...sort, corpus);
        expect(sortSettingsFromParams(params, corpus)).toEqual(sort);
    });
});

describe('pageFromParams', () => {
    it('should be the inverse of pageToParams', () => {
        const state: PageParameters = {
            from: 0,
            size: 20,
        };

        expect(pageFromParams(pageToParams(state))).toEqual(state);

        state.from = 40;
        expect(pageFromParams(pageToParams(state))).toEqual(state);
    });

    it('should use blank parameters for the default state', () => {
        const state: PageParameters = {
            from: 0,
            size: 20,
        };

        expect(pageToParams(state)).toEqual({ p: null });
        expect(pageFromParams({})).toEqual(state);
    });
});

describe('omitNullParameters', () => {
    it('should omit null parameters', () => {
        const p = { a: null, b: '1', c: 'test' };

        expect(omitNullParameters(p)).toEqual(
            { b: '1', c: 'test' }
        );
    });
});

describe('omitNullParameters', () => {
    it('should omit null parameters', () => {
        const p = { a: null, b: '1', c: 'test' };

        expect(omitNullParameters(p)).toEqual(
            { b: '1', c: 'test' }
        );
    });
});
