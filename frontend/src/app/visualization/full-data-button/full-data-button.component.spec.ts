import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { FullDataButtonComponent } from './full-data-button.component';
import { commonTestBed } from '@app/common-test-bed';

describe('FullDataButtonComponent', () => {
    let component: FullDataButtonComponent;
    let fixture: ComponentFixture<FullDataButtonComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
      }));

    beforeEach(() => {
        fixture = TestBed.createComponent(FullDataButtonComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
