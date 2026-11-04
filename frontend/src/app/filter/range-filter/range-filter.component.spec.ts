import { ComponentFixture, TestBed, fakeAsync, flushMicrotasks, waitForAsync } from '@angular/core/testing';

import { commonTestBed } from '@app/common-test-bed';

import { SearchService } from '@services';
import * as _ from 'lodash';
import { corpusFactory, floatFieldFactory, intFieldFactory } from '@mock-data/corpus';
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

    const initComponent = (min: number, max: number) => {
        const corpus = corpusFactory();
        corpus.fields.push(field);

        searchService = TestBed.inject(SearchService);
        fixture = TestBed.createComponent(RangeFilterComponent);
        component = fixture.componentInstance;
        component.queryModel = new QueryModel(corpus);
        component.filter = component.queryModel.filterForField(field) as RangeFilter;
        component.filter.set({ min, max });
        fixture.detectChanges();
    }

    describe('with integer field', () => {
        beforeEach(() => {
            field = intFieldFactory();
            initComponent(50, 60);
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

        it('calculates the step size', () => {
            const cases = [
                [0, 100, 1],
                [0, 250, 1],
                [0, 1500, 10],
                [0, 20, 1],
                [0, 3, 1],
            ];

            for (let [min, max, step] of cases) {
                expect(component.step(min, max)).toBeCloseTo(step);
            }
        });
    });

    describe('with float field', () => {
        beforeEach(() => {
            field = floatFieldFactory();
            initComponent(0.1, 1.0);
        });

        it('should create', () => {
            expect(component).toBeTruthy();
        });

        it('calculates the step size', () => {
            const cases = [
                [0, 100, 1],
                [0, 250, 1],
                [0, 1500, 10],
                [0, 20, 0.1],
                [0, 3, 0.01],
            ];

            for (let [min, max, step] of cases) {
                expect(component.step(min, max)).toBeCloseTo(step);
            }

        });
    });
});
