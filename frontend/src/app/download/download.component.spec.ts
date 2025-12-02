import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { corpusFactory } from '@mock-data/corpus';
import { commonTestBed } from '@app/common-test-bed';
import { QueryModel } from '@models';

import { DownloadComponent } from './download.component';
import { SimpleChange } from '@angular/core';

describe('DownloadComponent', () => {
    let component: DownloadComponent;
    let fixture: ComponentFixture<DownloadComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DownloadComponent);
        component = fixture.componentInstance;
        component.corpus = corpusFactory();
        component.queryModel = new QueryModel(component.corpus);
        component.ngOnChanges({
            queryModel: new SimpleChange(undefined, component.queryModel, true)
         });
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should respond to field selection', () => {
        // Start with a single field
        expect(component['getColumnNames']()).toEqual(['genre', 'content', 'date']);

        // Deselect all
        component.fieldSelection = [];
        expect(component['getColumnNames']()).toEqual([]);

        // Select two
        component.fieldSelection = ['genre', 'content'];
        expect(component['getColumnNames']()).toEqual(['genre', 'content']);
    });
});
