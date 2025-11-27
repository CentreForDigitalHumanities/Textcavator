import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { FieldInfoComponent } from './field-info.component';
import { commonTestBed } from '@app/common-test-bed';

describe('FieldInfoComponent', () => {
    let component: FieldInfoComponent;
    let fixture: ComponentFixture<FieldInfoComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(FieldInfoComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
