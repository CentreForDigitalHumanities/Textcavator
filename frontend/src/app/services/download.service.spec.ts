import { TestBed, inject } from '@angular/core/testing';

import { ApiService } from './api.service';
import { ApiServiceMock } from '@mock-data/api';
import { DownloadService } from './download.service';
import { corpusFactory } from '@mock-data/corpus';
import {
    DownloadOptions,
    LimitedResultsDownloadParameters,
    QueryModel,
    SortState,
} from '@models';

describe('DownloadService', () => {
    let apiService: ApiService;
    let service: DownloadService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: ApiService, useValue: new ApiServiceMock() },
                DownloadService,
            ]
        });
    });

    beforeEach(inject([ApiService, DownloadService], (api, download) => {
        service = download;
        apiService = api;
    }));

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    it('should make a download request', () => {
        const query = new QueryModel(corpusFactory());
        query.setQueryText('test');

        const size = 1;
        const route = `/search/${query.corpus.name}`;
        const sort: SortState = [query.corpus.fields[2], 'desc'];
        const options: DownloadOptions = {
            encoding: 'utf-8',
        };

        spyOn(apiService, 'download').and.returnValue(Promise.resolve({}));
        const fieldNames = query.corpus.fields.map(field => field.name)
        service.download(query.corpus, query, fieldNames, size, route, sort, undefined, options, []);
        const expectedBody: LimitedResultsDownloadParameters = {
            corpus: query.corpus.name,
            fields: ['genre', 'content', 'date'],
            route,
            es_query: {
                query: {
                    bool: {
                        must: {
                            simple_query_string: {
                                query: 'test',
                                lenient: true,
                                default_operator: 'or',
                            },
                        },
                        filter: [],
                    },
                },
                sort: [{ date: 'desc' }],
                from: 0,
                size,
            },
            encoding: 'utf-8',
            extra: [],
        };
        expect(apiService.download).toHaveBeenCalledWith(expectedBody);
    });
});
