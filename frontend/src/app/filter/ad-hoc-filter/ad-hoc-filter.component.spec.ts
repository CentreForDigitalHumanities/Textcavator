import { ComponentFixture, TestBed } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { AdHocFilterComponent } from './ad-hoc-filter.component';

describe('AdHocFilterComponent', () => {
    let component: AdHocFilterComponent;
    let fixture: ComponentFixture<AdHocFilterComponent>;

    beforeEach(async () => {
        commonTestBed().testingModule.compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(AdHocFilterComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
