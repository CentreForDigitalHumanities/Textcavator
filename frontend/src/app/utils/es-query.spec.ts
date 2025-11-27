/* eslint-disable @typescript-eslint/naming-convention */
import * as _ from 'lodash';
import { contentFieldFactory, corpusFactory, dateFieldFactory, keywordFieldFactory } from '@mock-data/corpus';
import {
    makeEsSearchClause, makeHighlightSpecification, makeSimpleQueryString, makeSortSpecification,
    resultsParamsToAPIQuery
} from './es-query';
import { CorpusField, QueryModel } from '@models';
import { PageResultsParameters } from '@models/page-results';
import { APIQuery } from '@models/search-requests';
import { isTagFilter } from '@models/tag-filter';
import { searchFieldOptions } from './search-fields';
import { findByName } from './utils';

describe('es-query utils', () => {
    it('should make a simple query string clause', () => {
        expect(makeSimpleQueryString('test', [contentFieldFactory()])).toEqual({
            simple_query_string: {
                query: 'test',
                lenient: true,
                default_operator: 'or',
                fields: ['content']
            }
        });
    });

    it('should set search fields', () => {
        const contentField = contentFieldFactory();
        const notesField = _.set(contentFieldFactory(), 'name', 'notes');

        const esQuery = makeEsSearchClause('test', [contentField, notesField]);
        expect(esQuery['simple_query_string'].fields).toEqual(['content', 'notes']);

        const esQuery2 = makeEsSearchClause('test', [contentField]);
        expect(esQuery2['simple_query_string'].fields).toEqual(['content']);

        const searchableKeywordField = keywordFieldFactory(true);
        const esQuery3 = makeEsSearchClause('test', [searchableKeywordField, contentField]);
        expect(esQuery3['simple_query_string'].fields).toEqual(['genre.text', 'content']);
    });

    it('should make a sort specification', () => {
        expect(makeSortSpecification(undefined, 'asc')).toEqual({});
        expect(makeSortSpecification(dateFieldFactory(), 'desc')).toEqual({
            sort: [{ date: 'desc' }]
        });
    });

    describe('makeHighlightSpecification', () => {
        it('should make a highlight specification', () => {
            expect(_.keys(
                makeHighlightSpecification(corpusFactory(), 'test', [], undefined)
            )).toEqual([]);
            expect(_.keys(
                makeHighlightSpecification(corpusFactory(), 'test', [], 100)
            )).toEqual(['highlight']);
        });


        it('should select highlight fields', () => {
            const corpus = corpusFactory();
            corpus.fields[0] = keywordFieldFactory(true); // corpus now has 2 searchable fields

            const highlightedFields = (spec) => spec.highlight.fields.map(f => _.keys(f)[0]);
            expect(highlightedFields(
                makeHighlightSpecification(corpus, 'test', [], 100)
            )).toContain('content')

            expect(highlightedFields(
                makeHighlightSpecification(corpus, 'test', [corpus.fields[0]], 100)
            )).not.toContain('content');
        });

        it('should select stemmed fields', () => {
            const corpus = corpusFactory();
            const makeSpec = (fields: CorpusField[]) =>
                makeHighlightSpecification(corpus, 'test', fields, 100);
            const matchedFields = spec => spec.highlight.fields[0].content.matched_fields;

            expect(matchedFields(makeSpec([]))).toEqual(['content', 'content.stemmed']);

            const searchFields = searchFieldOptions(corpus);
            const baseField = findByName(searchFields, 'content');
            const stemmedField = findByName(searchFields, 'content.stemmed');

            expect(matchedFields(makeSpec([baseField]))).toEqual(['content']);
            expect(matchedFields(makeSpec([stemmedField]))).toEqual(['content.stemmed']);

        })
    });

    it('should create an API query for paged results', () => {
        const queryModel = new QueryModel(corpusFactory());
        const tagFilter = queryModel.filters.find(isTagFilter);
        tagFilter.set([1]);
        queryModel.setQueryText('test');

        const dateField = queryModel.corpus.fields[2]
        const resultsParams: PageResultsParameters = {
            sort: [dateField, 'desc'],
            from: 0,
            size: 20,
        };

        const expected: APIQuery = {
            es_query: {
                query: {
                    bool: {
                        must: {
                            simple_query_string: {
                                query: 'test',
                                lenient: true,
                                default_operator: 'or',
                            }
                        },
                        filter: [],
                    }
                },
                size: 20,
                from: 0,
                sort: [
                    { date: 'desc'}
                ],
            },
            tags: [1],
        };

        expect(resultsParamsToAPIQuery(queryModel, resultsParams)).toEqual(expected);
    });
});
