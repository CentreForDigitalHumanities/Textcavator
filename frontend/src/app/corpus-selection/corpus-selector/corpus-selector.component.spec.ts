import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { CorpusSelectorComponent } from './corpus-selector.component';
import { commonTestBed } from '@app/common-test-bed';
import { corpusFactory } from '@mock-data/corpus';

describe('CorpusSelectorComponent', () => {
    let component: CorpusSelectorComponent;
    let fixture: ComponentFixture<CorpusSelectorComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(CorpusSelectorComponent);
        component = fixture.componentInstance;
        component.corpus = corpusFactory();
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
