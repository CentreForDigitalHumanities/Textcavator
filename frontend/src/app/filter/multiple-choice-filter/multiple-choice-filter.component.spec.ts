import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { corpusFactory, } from '@mock-data/corpus';

import { commonTestBed } from '@app/common-test-bed';
import { MultipleChoiceFilter, QueryModel } from '@models';

import { MultipleChoiceFilterComponent } from './multiple-choice-filter.component';
import * as _ from 'lodash';

describe('MultipleChoiceFilterComponent', () => {
    let component: MultipleChoiceFilterComponent;
    let fixture: ComponentFixture<MultipleChoiceFilterComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(MultipleChoiceFilterComponent);
        component = fixture.componentInstance;
        const corpus = corpusFactory();
        component.queryModel = new QueryModel(corpus);
        component.filter = component.queryModel.filterForField(corpus.fields[0]) as MultipleChoiceFilter;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
