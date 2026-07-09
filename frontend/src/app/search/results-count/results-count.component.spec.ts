import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { ResultsCountComponent } from './results-count.component';
import { commonTestBed } from '@app/common-test-bed';

describe('ResultsCountComponent', () => {
    let component: ResultsCountComponent;
    let fixture: ComponentFixture<ResultsCountComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ResultsCountComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
