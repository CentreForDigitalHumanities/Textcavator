import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { By } from '@angular/platform-browser';

import { commonTestBed } from '@app/common-test-bed';

import { FilterManagerComponent } from './filter-manager.component';
import { corpusFactory } from '@mock-data/corpus';
import { QueryModel } from '@models';

import { AuthService } from '@services';
import { UnauthenticatedMock } from '@mock-data/auth';

describe('FilterManagerComponent', () => {
    let component: FilterManagerComponent;
    let fixture: ComponentFixture<FilterManagerComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    describe('with authenticated user', () => {
        const corpus = corpusFactory();

        beforeEach(() => {
            fixture = TestBed.createComponent(FilterManagerComponent);
            component = fixture.componentInstance;
            component.queryModel = new QueryModel(corpus);
            fixture.detectChanges();
        });

        it('should create', () => {
            expect(component).toBeTruthy();
            expect(component.filters.length).toEqual(4); // one per field, plus tags
        });

        it('resets filters when corpus changes', () => {
            const newCorpus = corpusFactory();
            newCorpus.fields[0].filterOptions = null;
            newCorpus.fields = newCorpus.fields.slice(0, 1);

            component.queryModel = new QueryModel(newCorpus);
            fixture.detectChanges();
            expect(component.filters.length).toEqual(2);
            expect(component.filters[0]['adHoc']).toBeTrue();
            component.queryModel = new QueryModel(corpus);
            fixture.detectChanges();
            expect(component.filters.length).toEqual(4);
            expect(component.filters[0]['adHoc']).toBeFalse();
        });

        it('toggles filters on and off', async () => {
            const filter = component.filters.find(f => f['corpusField']['name'] === 'genre');
            expect(component.activeFilters.length).toBe(0);
            filter.set(['Fantasy']);
            expect(component.activeFilters.length).toBe(1);
            filter.toggle();
            expect(component.activeFilters.length).toBe(0);
            filter.toggle();
            expect(component.activeFilters.length).toBe(1);
        });

        it('shows tag filter', async () => {
            await fixture.whenStable();
            const compiled = fixture.debugElement;
            const tagFilter = compiled.query(By.css('ia-tag-filter'));
            expect(tagFilter).toBeTruthy();
        });
    });

    describe('with unauthenticated user', () => {
        beforeEach(() => {
            TestBed.overrideProvider(AuthService, {useValue: new UnauthenticatedMock()});
            fixture = TestBed.createComponent(FilterManagerComponent);
            component = fixture.componentInstance;
            component.queryModel = new QueryModel(corpusFactory());
            fixture.detectChanges();
        });

        it('does not show tag filter', async () => {
            await fixture.whenStable();
            const compiled = fixture.debugElement;
            const tagFilter = compiled.query(By.css('ia-tag-filter'));
            expect(tagFilter).not.toBeTruthy();
        });
    });


});
