import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { DocumentPageComponent } from './document-page.component';
import { makeDocument } from '@mock-data/constructor-helpers';

describe('DocumentPageComponent', () => {
    let component: DocumentPageComponent;
    let fixture: ComponentFixture<DocumentPageComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DocumentPageComponent);
        component = fixture.componentInstance;
        component.document = makeDocument({great_field: 'Hello world!'});
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
