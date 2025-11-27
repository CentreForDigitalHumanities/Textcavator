import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { DefinitionJsonUploadComponent } from './definition-json-upload.component';
import { ApiService } from '@services';
import { ApiServiceMock } from 'mock-data/api';
import { SharedModule } from '@shared/shared.module';

describe('DefinitionJsonUploadComponent', () => {
    let component: DefinitionJsonUploadComponent;
    let fixture: ComponentFixture<DefinitionJsonUploadComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [DefinitionJsonUploadComponent],
            imports: [SharedModule],
            providers: [
                { provide: ApiService, useClass: ApiServiceMock },
            ],
        })
            .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(DefinitionJsonUploadComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
