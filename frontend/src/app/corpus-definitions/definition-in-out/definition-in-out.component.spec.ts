import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DefinitionInOutComponent } from './definition-in-out.component';
import { DefinitionJsonUploadComponent } from '../definition-json-upload/definition-json-upload.component';
import { SharedModule } from '@shared/shared.module';
import { ApiService, CorpusService } from '@services';
import { ApiServiceMock } from 'mock-data/api';
import { ActivatedRoute } from '@angular/router';
import { CorpusServiceMock } from '@mock-data/corpus';

describe('DefinitionInOutComponent', () => {
    let component: DefinitionInOutComponent;
    let fixture: ComponentFixture<DefinitionInOutComponent>;

    const mockRoute = { snapshot: { params: {corpusID: 1} } };

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [DefinitionInOutComponent, DefinitionJsonUploadComponent],
            imports: [SharedModule],
            providers: [
                { provide: ApiService, useClass: ApiServiceMock },
                { provide: ActivatedRoute, useValue: mockRoute },
                { provide: CorpusService, useClass: CorpusServiceMock },
            ],
        })
            .compileComponents();
    });


    beforeEach(() => {
        fixture = TestBed.createComponent(DefinitionInOutComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
