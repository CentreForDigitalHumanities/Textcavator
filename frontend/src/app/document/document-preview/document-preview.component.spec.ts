import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { DocumentPreviewComponent } from './document-preview.component';
import { commonTestBed } from '@app/common-test-bed';
import { contentFieldFactory } from '@mock-data/corpus';
import { makeDocument } from '@mock-data/constructor-helpers';
import { DocumentPage } from '@models/document-page';

describe('DocumentPreviewComponent', () => {
    let component: DocumentPreviewComponent;
    let fixture: ComponentFixture<DocumentPreviewComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DocumentPreviewComponent);
        component = fixture.componentInstance;
        component.document = makeDocument({ content: 'Hello world!' });
        component.page = new DocumentPage([component.document], 1, [contentFieldFactory()]);
        fixture.detectChanges();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(DocumentPreviewComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
