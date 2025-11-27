import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContentFieldPreviewComponent } from './content-field-preview.component';
import { commonTestBed } from '@app/common-test-bed';

describe('ContentFieldPreviewComponent', () => {
    let component: ContentFieldPreviewComponent;
    let fixture: ComponentFixture<ContentFieldPreviewComponent>;

    beforeEach(async () => {
        await commonTestBed().testingModule.compileComponents();

        fixture = TestBed.createComponent(ContentFieldPreviewComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
