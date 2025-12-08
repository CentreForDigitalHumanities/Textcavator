import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DocumentTagsComponent } from './document-tags.component';
import { commonTestBed } from '@app/common-test-bed';
import { makeDocument } from '@mock-data/constructor-helpers';

describe('DocumentTagsComponent', () => {
    let component: DocumentTagsComponent;
    let fixture: ComponentFixture<DocumentTagsComponent>;

    beforeEach(async () => {
        commonTestBed().testingModule.compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(DocumentTagsComponent);
        component = fixture.componentInstance;
        component.document = makeDocument({great_field: 'test'});
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
