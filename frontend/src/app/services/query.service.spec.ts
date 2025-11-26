import { TestBed, inject } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { ApiService } from './api.service';
import { ApiServiceMock } from '@mock-data/api';
import { ApiRetryService } from './api-retry.service';
import { QueryService } from './query.service';
import { SessionService } from './session.service';
import { appRoutes } from 'app/app.module';

describe('QueryService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                QueryService,
                ApiRetryService,
                { provide: ApiService, useValue: new ApiServiceMock() },
                SessionService,
                provideRouter(appRoutes)
            ],
        });
    });

    it('should be created', inject([QueryService], (service: QueryService) => {
        expect(service).toBeTruthy();
    }));
});
