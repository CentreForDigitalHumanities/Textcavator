import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { ApiService } from '@services/api.service';
import { ApiServiceMock } from '@mock-data/api';
import { SessionService } from '@services/session.service';

import { VerifyEmailComponent } from './verify-email.component';
import { appRoutes } from 'app/app.module';

describe('VerifyEmailComponent', () => {
    let component: VerifyEmailComponent;
    let fixture: ComponentFixture<VerifyEmailComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [VerifyEmailComponent],
            providers: [
                SessionService,
                { provide: ApiService, useValue: new ApiServiceMock() },
                provideRouter(appRoutes)
            ],
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(VerifyEmailComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
