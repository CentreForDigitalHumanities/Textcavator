import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { QueryModel } from '@models';
import { corpusFactory } from '@mock-data/corpus';
import { commonTestBed } from '@app/common-test-bed';

import { QueryFiltersComponent } from './query-filters.component';

describe('QueryFiltersComponent', () => {
    let component: QueryFiltersComponent;
    let fixture: ComponentFixture<QueryFiltersComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(QueryFiltersComponent);
        component = fixture.componentInstance;
        component.queryModel = new QueryModel(corpusFactory());
        component.queryModel.setQueryText('testing');
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
