import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { ApiServiceMock } from '@mock-data/api';
import { ApiService } from './api.service';

import { AuthService } from './auth.service';
import { SessionService } from './session.service';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { appRoutes } from 'app/app.module';

describe('AuthService', () => {
    let service: AuthService;

    beforeEach(() => {
        TestBed.configureTestingModule({
    providers: [
        SessionService,
        { provide: ApiService, useValue: new ApiServiceMock() },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
        provideRouter(appRoutes)
    ]
});
        service = TestBed.inject(AuthService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

});
