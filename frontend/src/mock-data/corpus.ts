/* eslint-disable @typescript-eslint/naming-convention */
import { of } from 'rxjs';
import { Corpus, CorpusField } from '../app/models';


export const keywordFieldFactory = (searchable = false): CorpusField =>
    new CorpusField({
        name: 'genre',
        description: 'Genre of the document',
        display_name: 'Genre',
        display_type: 'keyword',
        es_mapping: searchable ?
            { type: 'keyword', fields: { text: { type: 'text'}}} :
            { type: 'keyword'},
        hidden: false,
        searchable,
        downloadable: true,
        search_filter: {
            name: 'MultipleChoiceFilter',
            option_count: 10,
            description: 'Select genre',
        },
        results_overview: true,
        search_field_core: false,
        csv_core: true,
        visualizations: ['resultscount', 'termfrequency'],
        visualization_sort: '',
        language: '',
        sortable: false,
        indexed: true,
        required: false,
    });


export const contentFieldFactory = (): CorpusField =>
    new CorpusField({
        name: 'content',
        description: 'Text of the document',
        display_name: 'Content',
        display_type: 'text_content',
        es_mapping: {
            type: 'text',
            term_vector: 'with_positions_offsets',
            fields: {
                length: { type: 'token_count', analyzer: 'standard' },
                clean: { type: 'text', analyzer: 'clean_en', term_vector: 'with_positions_offsets' },
                stemmed: { type: 'text', analyzer: 'stemmed_en', term_vector: 'with_positions_offsets' },
            },
        },
        hidden: false,
        sortable: false,
        searchable: true,
        downloadable: true,
        search_filter: null,
        results_overview: true,
        search_field_core: true,
        csv_core: true,
        visualizations: ['wordcloud', 'ngram'],
        visualization_sort: null,
        indexed: true,
        required: false,
        language: 'eng',
    });


export const dateFieldFactory = () =>
    new CorpusField({
        name: 'date',
        display_name: 'Date',
        description: 'Publication date for the document',
        display_type: 'date',
        hidden: false,
        sortable: true,
        searchable: false,
        downloadable: true,
        search_filter: {
            name: 'DateFilter',
            lower: '1800-01-01',
            upper: '1899-12-31',
            description: 'Select date range for documents'
        },
        es_mapping: {type: 'date'},
        results_overview: true,
        search_field_core: false,
        csv_core: true,
        visualizations: ['resultscount', 'termfrequency'],
        visualization_sort: null,
        indexed: true,
        required: false,
        language: '',
    });


export const intFieldFactory = () =>
    new CorpusField({
        name: 'page',
        display_name: 'Page',
        description: 'Page number of the document',
        display_type: 'integer',
        hidden: false,
        sortable: true,
        downloadable: true,
        search_filter: {
            name: 'RangeFilter',
            lower: 0,
            upper: 100,
            description: 'Select page range',
        },
        es_mapping: { type: 'integer' },
        results_overview: false,
        searchable: false,
        search_field_core: false,
        csv_core: false,
        visualizations: ['resultscount', 'termfrequency'],
        visualization_sort: '',
        indexed: true,
        required: false,
        language: '',
    });

export const booleanFieldFactory = () =>
    new CorpusField({
        name: 'public_domain',
        display_name: 'In public domain',
        description: 'Whether the text is in the public domain',
        display_type: 'boolean',
        hidden: false,
        sortable: false,
        downloadable: true,
        search_filter: {
            name: 'BooleanFilter',
            description: ''
        },
        es_mapping: { type: 'boolean' },
        results_overview: false,
        searchable: false,
        search_field_core: false,
        csv_core: false,
        visualizations: [],
        visualization_sort: '',
        indexed: true,
        required: false,
        language: '',
    });


export const corpusFactory = () =>
    new Corpus(
        1,
        'test',
        'Test corpus',
        'A basic corpus for testing',
        [
            keywordFieldFactory(),
            contentFieldFactory(),
            dateFieldFactory(),
        ],
        1800,
        1900,
        '',
        true,
        false,
        ['English'],
        'Books',
        false,
        { contextFields: [], displayName: null },
        [undefined, 'desc'],
    );


export class CorpusServiceMock {
    public corporaPromise = Promise.resolve([corpusFactory()]);
    public currentCorpus = of(corpusFactory());

    public get(): Promise<Corpus[]> {
        return this.corporaPromise;
    }
}
