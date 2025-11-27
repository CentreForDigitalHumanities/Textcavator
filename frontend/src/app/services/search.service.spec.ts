import { TestBed, inject } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';

import { ApiService } from './api.service';
import { ApiServiceMock } from '@mock-data/api';
import { ApiRetryService } from './api-retry.service';
import { ElasticSearchService } from './elastic-search.service';
import { ElasticSearchServiceMock } from '@mock-data/elastic-search';
import { QueryService } from './query.service';
import { SearchService } from './search.service';
import { SessionService } from './session.service';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { QueryModel } from '@models';
import { corpusFactory } from '@mock-data/corpus';
import { AuthService } from './auth.service';
import { AuthServiceMock } from '@mock-data/auth';
import { appRoutes } from 'app/app.module';


describe('SearchService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
    providers: [
        SearchService,
        ApiRetryService,
        { provide: AuthService, useValue: new AuthServiceMock() },
        { provide: ApiService, useValue: new ApiServiceMock() },
        {
            provide: ElasticSearchService,
            useValue: new ElasticSearchServiceMock(),
        },
        QueryService,
        SessionService,
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
        provideRouter(appRoutes)
    ]
});
    });

    it('should be created', inject([SearchService], (service: SearchService) => {
        expect(service).toBeTruthy();
    }));

    it('should search', inject([SearchService], async (service: SearchService) => {
        const queryModel = new QueryModel(corpusFactory());
        const results = await service.loadResults(queryModel, {from: 0, size: 20, sort: [undefined, 'desc']});
        expect(results).toBeTruthy();
        expect(results.total.value).toBeGreaterThan(0);
    }));

});
