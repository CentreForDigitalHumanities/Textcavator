
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TagSelectComponent } from './tag-select.component';
import { commonTestBed } from '@app/common-test-bed';

describe('TagSelectComponent', () => {
    let component: TagSelectComponent;
    let fixture: ComponentFixture<TagSelectComponent>;

    beforeEach(async () => {
        commonTestBed().testingModule.compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(TagSelectComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
