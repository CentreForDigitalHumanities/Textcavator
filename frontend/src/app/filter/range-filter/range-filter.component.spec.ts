import { ComponentFixture, TestBed, fakeAsync, flushMicrotasks, waitForAsync } from '@angular/core/testing';

import { commonTestBed } from '@app/common-test-bed';

import { SearchService } from '@services';
import * as _ from 'lodash';
import { corpusFactory, intFieldFactory } from '@mock-data/corpus';
import { CorpusField, QueryModel, RangeFilter } from '@models';
import { SimpleStore } from '@app/store/simple-store';
import { RangeFilterComponent } from './range-filter.component';

describe('RangeFilterComponent', () => {
    let component: RangeFilterComponent;
    let searchService: SearchService;
    let fixture: ComponentFixture<RangeFilterComponent>;
    let field: CorpusField;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        const corpus = corpusFactory();
        field = intFieldFactory();
        corpus.fields.push(field);

        searchService = TestBed.inject(SearchService);
        fixture = TestBed.createComponent(RangeFilterComponent);
        component = fixture.componentInstance;
        component.queryModel = new QueryModel(corpus);
        component.filter = component.queryModel.filterForField(field) as RangeFilter;
        component.filter.set({ min: 50, max: 60 });
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should use the specified data range', fakeAsync(() => {
        const newFilter = new RangeFilter(new SimpleStore(), field);
        component.onFilterSet(newFilter);

        flushMicrotasks();

        expect(component.min).toEqual(0);
        expect(component.max).toEqual(100);
    }));


    it('should fetch the data range when not specified', fakeAsync(() => {
        const min = 300;
        const max = 400;
        spyOn(searchService, 'aggregateSearch').and.returnValues(
            Promise.resolve(min), Promise.resolve(max)
        );

        field.filterOptions = {
            name: 'RangeFilter',
            lower: null,
            upper: null,
            description: ''
        };

        const newFilter = new RangeFilter(new SimpleStore(), field);
        component.onFilterSet(newFilter);

        flushMicrotasks();

        expect(component.min).toEqual(min);
        expect(component.max).toEqual(max);
    }));
});
