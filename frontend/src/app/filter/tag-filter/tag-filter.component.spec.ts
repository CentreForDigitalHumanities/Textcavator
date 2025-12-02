import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { TagFilterComponent } from './tag-filter.component';
import { commonTestBed } from '@app/common-test-bed';

describe('TagFilterComponent', () => {
    let component: TagFilterComponent;
    let fixture: ComponentFixture<TagFilterComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(TagFilterComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
