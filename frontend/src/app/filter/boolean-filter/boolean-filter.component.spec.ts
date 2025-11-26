import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { booleanFieldFactory, corpusFactory } from '@mock-data/corpus';

import { commonTestBed } from '@app/common-test-bed';
import { BooleanFilter, CorpusField, QueryModel } from '@models';
import { BooleanFilterComponent } from './boolean-filter.component';
import { By } from '@angular/platform-browser';

describe('BooleanFilterComponent', () => {
    let component: BooleanFilterComponent;
    let fixture: ComponentFixture<BooleanFilterComponent>;
    let field: CorpusField;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(BooleanFilterComponent);
        component = fixture.componentInstance;
        field = booleanFieldFactory();
        const corpus = corpusFactory();
        corpus.fields.push(field);
        component.queryModel = new QueryModel(corpus);
        component.filter = component.queryModel.filterForField(field) as BooleanFilter;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should handle update events', () => {
        // trigger onchange of the dropdown
        const dropdown = fixture.debugElement.query(By.css('ia-dropdown'));
        const triggerDropdown = (value: boolean) => {
            dropdown.triggerEventHandler('onChange', value);
        };

        spyOn(component, 'update');
        triggerDropdown(true);
        expect(component.update).toHaveBeenCalledOnceWith(true);

        triggerDropdown(false);
        expect(component.update).toHaveBeenCalledTimes(2);
        expect(component.update).toHaveBeenCalledWith(false);
    });
});
