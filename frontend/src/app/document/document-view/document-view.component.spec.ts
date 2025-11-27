import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import * as _ from 'lodash';
import { corpusFactory } from '@mock-data/corpus';

import { commonTestBed } from '@app/common-test-bed';

import { DocumentViewComponent } from './document-view.component';
import { makeDocument } from '@mock-data/constructor-helpers';

describe('DocumentViewComponent', () => {
    let component: DocumentViewComponent;
    let fixture: ComponentFixture<DocumentViewComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DocumentViewComponent);
        component = fixture.componentInstance;
        component.corpus = corpusFactory();
        component.corpus.scanImageType = 'image/png';
        component.document = makeDocument();
        fixture.detectChanges();
    });

    it('should be created', () => {
        expect(component).toBeTruthy();
    });

    it('should render metadata fields', () => {
        expect(component.propertyFields).toEqual([
            component.corpus.fields[0],
            component.corpus.fields[2]
        ]);
        const debug = fixture.debugElement.queryAll(By.css('[data-test-field-value]'));
        expect(debug.length).toEqual(2); // number of fields
        const element = debug[0].nativeElement as Element;
        expect(element.textContent.trim()).toBe('Science Fiction');
    });

    it('should create tabs', () => {
        const debug = fixture.debugElement.queryAll(By.css('[role=tab]'));
        expect(debug.length).toBe(2);
        expect(debug[0].attributes['id']).toBe('tab-field-content');
        expect(debug[1].attributes['id']).toBe('tab-scan');
    });

    it('shows named entities if showEntities is true', async () => {
        expect(fixture.debugElement.query(By.css('ia-entity-legend'))).toBeFalsy();
        component.showEntities = true;
        fixture.detectChanges();
        await fixture.whenStable();
        fixture.detectChanges();
        expect(fixture.debugElement.query(By.css('ia-entity-legend'))).toBeTruthy();
    });

});
