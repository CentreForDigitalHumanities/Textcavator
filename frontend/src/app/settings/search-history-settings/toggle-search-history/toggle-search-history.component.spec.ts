import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { ToggleSearchHistoryComponent } from './toggle-search-history.component';
import { commonTestBed } from '@app/common-test-bed';

describe('ToggleSearchHistoryComponent', () => {
    let component: ToggleSearchHistoryComponent;
    let fixture: ComponentFixture<ToggleSearchHistoryComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ToggleSearchHistoryComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
