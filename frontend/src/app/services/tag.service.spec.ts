import { TestBed } from '@angular/core/testing';

import { TagService } from './tag.service';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ApiService } from './api.service';
import { ApiServiceMock } from '@mock-data/api';
import { AuthService } from './auth.service';
import { AuthServiceMock } from '@mock-data/auth';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';

describe('TagService', () => {
    let service: TagService;

    beforeEach(() => {
        TestBed.configureTestingModule({
    imports: [],
    providers: [
        { provide: ApiService, useValue: new ApiServiceMock() },
        { provide: AuthService, useValue: new AuthServiceMock() },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
});
        service = TestBed.inject(TagService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
