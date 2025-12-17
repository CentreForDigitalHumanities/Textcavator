import { TestBed, inject } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { ApiServiceMock } from '@mock-data/api';
import { ApiService } from './api.service';
import { ApiRetryService } from './api-retry.service';
import { CorpusService } from './corpus.service';
import { SessionService } from './session.service';

import * as _ from 'lodash';
import { appRoutes } from 'app/app.module';

describe('CorpusService', () => {
    let service: CorpusService;
    const apiServiceMock = new ApiServiceMock();


    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                ApiRetryService,
                { provide: ApiService, useValue: apiServiceMock },
                CorpusService,
                SessionService,
                provideRouter(appRoutes)
            ],
        });
        service = TestBed.inject(CorpusService);
    });

    it('should be created', inject(
        [CorpusService],
        (corpusService: CorpusService) => {
            expect(corpusService).toBeTruthy();
        }
    ));

    it('should parse the list of corpora', async () => {
        apiServiceMock.fakeResult['corpus'] = [
            {
                name: 'test1',
                title: 'Test 1',
                description: 'Test description 1.',
                es_index: 'test1',
                overview_fields: [],
                fields: [],
                max_year: 2010,
                min_year: 1785,
                scan_image_type: 'png',
                allow_image_download: false,
                word_models_present: false,
            },
            {
                name: 'test2',
                title: 'Test 2',
                description: 'Test description 2.',
                es_index: 'test2',
                overview_fields: [],
                fields: [],
                max_year: 2010,
                min_year: 1785,
                scan_image_type: 'jpg',
                allow_image_download: true,
                word_models_present: true,
            },
        ];
        const items = await service.get();
        expect(items.map((item) => item.name)).toEqual(['test1', 'test2']);
    });

    it('should parse fields', () => {
        apiServiceMock.fakeResult['corpus'] = [
            {
                name: 'times',
                server_name: 'default',
                title: 'Times',
                description: 'This is a description.',
                es_index: 'times',
                languages: ['English'],
                category: 'Tests',
                default_sort: {
                    field: 'year',
                    ascending: false
                },
                fields: [
                    {
                        description:
                            'Banking concern to which the report belongs.',
                        es_mapping: { type: 'keyword' },
                        hidden: true,
                        sortable: false,
                        searchable: true,
                        downloadable: false,
                        name: 'bank',
                        display_name: 'Bank',
                        results_overview: false,
                        csv_core: false,
                        search_field_core: false,
                        visualizations: ['resultscount', 'termfrequency'],
                        visualization_sort: 'key',
                        search_filter: {
                            name: 'MultipleChoiceFilter',
                            description: 'Search only within these banks.',
                            fieldName: 'bank',
                            useAsFilter: false,
                            option_count: 42,
                        },
                    },
                    {
                        description: 'Year of the financial report.',
                        es_mapping: { type: 'integer' },
                        hidden: false,
                        sortable: true,
                        searchable: false,
                        downloadable: true,
                        name: 'year',
                        results_overview: true,
                        csv_core: true,
                        search_field_core: false,
                        histogram: false,
                        visualizations: ['resultscount', 'termfrequency'],
                        visualization_sort: 'key',
                        search_filter: {
                            name: 'RangeFilter',
                            description:
                                'Restrict the years from which search results will be returned.',
                            fieldName: 'year',
                            useAsFilter: false,
                            lower: 1785,
                            upper: 2010,
                        },
                    },
                    {
                        // example from people & parliament
                        description: 'The transcribed speech',
                        display_name: 'Speech',
                        display_type: 'text_content',
                        es_mapping: {
                            type: 'text',
                            term_vector: 'with_positions_offsets',
                            analyzer: 'standard',
                            fields: {
                                clean: {
                                    type: 'text',
                                    analyzer: 'clean',
                                    term_vector: 'with_positions_offsets',
                                },
                                stemmed: {
                                    type: 'text',
                                    analyzer: 'stemmed',
                                    term_vector: 'with_positions_offsets',
                                },
                                length: {
                                    type: 'token_count',
                                    analyzer: 'standard',
                                },
                            },
                        },
                        hidden: false,
                        indexed: true,
                        sortable: false,
                        searchable: true,
                        downloadable: true,
                        name: 'speech',
                        results_overview: true,
                        csv_core: false,
                        search_field_core: true,
                        term_frequency: false,
                        visualizations: ['wordcloud', 'ngram'],
                        visualization_sort: null,
                    },
                ],
                min_year: 1785,
                max_year: 2010,
                image: '/static/no-image.jpg',
                scan_image_type: 'png',
                allow_image_download: false,
                word_models_present: true,
            },
        ];

        return service.get().then((items) => {
            expect(items.length).toBe(1);
            const corpus = _.first(items);

            expect(corpus.scanImageType).toBe('png');

            const fieldData = [
                {
                    description: 'Banking concern to which the report belongs.',
                    displayName: 'Bank',
                    displayType: 'keyword',
                    resultsOverview: false,
                    csvCore: false,
                    searchFieldCore: false,
                    visualizations: ['resultscount', 'termfrequency'],
                    visualizationSort: 'key',
                    multiFields: undefined,
                    hidden: true,
                    sortable: false,
                    searchable: true,
                    downloadable: false,
                    name: 'bank',
                    filterOptions: {
                        name: 'MultipleChoiceFilter',
                        description: 'Search only within these banks.',
                        option_count: 42,
                    },
                    mappingType: 'keyword',
                },
                {
                    description: 'Year of the financial report.',
                    hidden: false,
                    sortable: true,
                    searchable: false,
                    downloadable: true,
                    name: 'year',
                    displayName: 'year',
                    displayType: 'integer',
                    resultsOverview: true,
                    csvCore: true,
                    searchFieldCore: false,
                    visualizations: ['resultscount', 'termfrequency'],
                    visualizationSort: 'key',
                    multiFields: undefined,
                    filterOptions: {
                        description:
                            'Restrict the years from which search results will be returned.',
                        name: 'RangeFilter',
                        lower: 1785,
                        upper: 2010,

                    },
                    mappingType: 'integer',
                },
                {
                    description: 'The transcribed speech',
                    hidden: false,
                    sortable: false,
                    searchable: true,
                    downloadable: true,
                    name: 'speech',
                    displayName: 'Speech',
                    displayType: 'text_content',
                    resultsOverview: true,
                    csvCore: false,
                    visualizations: ['wordcloud', 'ngram'],
                    visualizationSort: null,
                    multiFields: ['clean', 'stemmed', 'length'],
                    filterOptions: null,
                    searchFieldCore: true,
                    mappingType: 'text',
                },
            ];

            _.zip(corpus.fields, fieldData).map(([result, expected]) => {
                _.mapKeys(expected, key => {
                    expect(result[key]).toEqual(expected[key]);
                });
            });

        });
    });
});
