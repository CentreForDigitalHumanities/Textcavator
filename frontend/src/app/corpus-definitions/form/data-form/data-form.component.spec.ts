import { ComponentFixture, TestBed } from '@angular/core/testing';

import { commonTestBed } from '@app/common-test-bed';
import { CorpusDefinition } from '@models/corpus-definition';
import { ApiService, CorpusService } from '@services';
import { CorpusDefinitionService } from 'app/corpus-definitions/corpus-definition.service';
import { DataFormComponent } from './data-form.component';

describe('DataFormComponent', () => {
    let apiService: ApiService;
    let corpusService: CorpusService;
    let corpusDefinitionService: CorpusDefinitionService;
    let component: DataFormComponent;
    let fixture: ComponentFixture<DataFormComponent>;

    beforeEach(async () => {
        commonTestBed().testingModule.compileComponents();
        apiService = TestBed.inject(ApiService);
        corpusService = TestBed.inject(CorpusService);
        corpusDefinitionService = TestBed.inject(CorpusDefinitionService);
        corpusDefinitionService.setCorpus(new CorpusDefinition(apiService, corpusService, 1));

        fixture = TestBed.createComponent(DataFormComponent);
        component = fixture.componentInstance;

        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
