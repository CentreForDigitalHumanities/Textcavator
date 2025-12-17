/* eslint-disable @typescript-eslint/naming-convention */

import * as _ from 'lodash';
import {
    BooleanQuery,
    Corpus,
    CorpusField,
    EsFilter,
    EsSearchClause,
    FilterInterface,
    MatchAll,
    QueryModel,
    SimpleQueryString,
    SortBy,
    SortDirection,
} from '@models';
import { EsQuery } from '@models';
import { findByName } from './utils';
import { SearchFilter } from '@models/field-filter';
import { APIQuery } from '@models/search-requests';
import { TagFilter } from '@models/tag-filter';
import { PageResultsParameters } from '@models/page-results';
import { SimpleStore } from '../store/simple-store';
import { searchFieldOptions } from './search-fields';

// conversion from query model -> elasticsearch query language

export const matchAll: MatchAll = {
    match_all: {}
};

export const makeSimpleQueryString = (queryText: string, searchFields?: CorpusField[]): SimpleQueryString => {
    const clause: SimpleQueryString = {
        simple_query_string: {
            query: queryText,
            lenient: true,
            default_operator: 'or'
        }
    };
    if (searchFields) {
        _.set(clause, 'simple_query_string.fields', searchFields.map(searchFieldName));
    }
    return clause;
};

const searchFieldName = (field: CorpusField): string => {
    if (field.multiFields?.includes('text')) {
        return `${field.name}.text`;
    } else {
        return field.name;
    }
};

export const makeEsSearchClause = (queryText?: string, searchFields?: CorpusField[]): EsSearchClause => {
    if (queryText) {
        return makeSimpleQueryString(queryText, searchFields);
    } else {
        return matchAll;
    }
};

export const makeBooleanQuery = (query: EsSearchClause, filters: EsFilter[]): BooleanQuery => ({
    bool: {
        must: query,
        filter: filters,
    }
});

export const combineSearchClauseAndFilters = (queryText: string, filters: EsFilter[], searchFields?: CorpusField[]): EsQuery => {
    let query: MatchAll | BooleanQuery;
    if (queryText || filters.length) {
        const searchClause = makeEsSearchClause(queryText, searchFields);
        query = makeBooleanQuery(searchClause, filters);
    } else {
        query = matchAll;
    }
    return { query };
};

export const makeSortSpecification = (sortBy: SortBy, sortDirection: SortDirection) => {
    if (!sortBy) {
        return {};
    } else {
        const sortByField = {
            [sortBy.name]: sortDirection
        };
        return {
            sort: [sortByField]
        };
    }
};

const highlightFieldNames = (corpus: Corpus, searchFields?: CorpusField[]): string[]  => {
    const fields = searchFields?.length ? searchFields : searchFieldOptions(corpus);
    return fields.map(f => f.name);
};

const baseFieldName = (searchFieldName: string): string =>
    searchFieldName.split('.')[0];

const includeHighlight = (field: CorpusField, highlightFields: string[]): boolean =>
    _.some(highlightFields, f => baseFieldName(f) == field.name);

const makeFieldHighlightSpec = (field: CorpusField, highlightFields: string[]) => {
    const spec = {};
    if (field.fastVectorHighlight) {
        spec['type'] = 'fvh';
    }
    if (field.multiFields) {
        spec['matched_fields'] = highlightFields.filter(f => baseFieldName(f) == field.name);
    }
    return { [field.name]: spec };
};

export const highlightPreTag = '<mark class="highlight">';
export const highlightPostTag = '</mark>';

export const makeHighlightSpecification = (corpus: Corpus, queryText: string | undefined, searchFields: CorpusField[], highlightSize?: number) => {
    if (!queryText || !highlightSize) {
        return {};
    }
    const highlightFields = highlightFieldNames(corpus, searchFields);

    return {
        highlight: {
            fragment_size: highlightSize,
            pre_tags: [highlightPreTag],
            post_tags: [highlightPostTag],
            order: 'score',
            fields: corpus.fields
                .filter(f => includeHighlight(f, highlightFields))
                .map(f => makeFieldHighlightSpec(f, highlightFields)),
        },
    };
};

// conversion from elasticsearch query language -> query model

export const apiQueryToQueryModel = (query: APIQuery, corpus: Corpus): QueryModel => {
    const esQuery = 'es_query' in query ? query.es_query : query; // fix for legacy queries
    const model = esQueryToQueryModel(esQuery, corpus);
    if (query.tags) {
        const store = new SimpleStore();
        const tagFilter = new TagFilter(store);
        tagFilter.set(query.tags);
        model.addFilter(tagFilter);
    }
    return model;
};

export const esQueryToQueryModel = (query: EsQuery, corpus: Corpus): QueryModel => {
    const model = new QueryModel(corpus);
    model.setQueryText(queryTextFromEsSearchClause(query.query));
    const filters = filtersFromEsQuery(query, corpus);
    filters.forEach(filter => model.addFilter(filter));
    return model;
};

const queryTextFromEsSearchClause = (query: EsSearchClause | BooleanQuery | EsFilter): string => {
    const clause = 'bool' in query ? query.bool.must : query;

    if ('simple_query_string' in clause) {
        return clause.simple_query_string.query;
    }
};

const filtersFromEsQuery = (query: EsQuery, corpus: Corpus): SearchFilter[] => {
    if ('bool' in query.query) {
        const filters = query.query.bool.filter;
        return filters.map(filter => esFilterToSearchFilter(filter, corpus));
    }
    return [];
};

const esFilterToSearchFilter = (esFilter: EsFilter, corpus: Corpus): SearchFilter => {
    const filterType = _.first(_.keys(esFilter)) as 'term'|'terms'|'range';
    const fieldName = _.first(_.keys(esFilter[filterType]));
    const field = findByName(corpus.fields, fieldName);
    const filter = field.makeSearchFilter();
    filter.set(filter.dataFromEsFilter(esFilter as any)); // we know that the esFilter is of the correct type
    return filter;
};

export const resultsParamsToAPIQuery = (queryModel: QueryModel, params: PageResultsParameters): APIQuery => {
    const query = queryModel.toAPIQuery();

    const sort = makeSortSpecification(...params.sort);
    const highlight = makeHighlightSpecification(queryModel.corpus, queryModel.queryText, queryModel.searchFields, params.highlight);
    const addToQuery = {
        es_query: {
            ...sort,
            ...highlight,
            from: params.from,
            size: params.size,
        }
    };
    _.merge(query, addToQuery);

    return query;
};
