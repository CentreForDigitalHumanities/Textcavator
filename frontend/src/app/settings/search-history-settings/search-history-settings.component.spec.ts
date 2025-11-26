import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { SearchHistorySettingsComponent } from './search-history-settings.component';
import { commonTestBed } from '@app/common-test-bed';

describe('SearchHistorySettingsComponent', () => {
    let component: SearchHistorySettingsComponent;
    let fixture: ComponentFixture<SearchHistorySettingsComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(SearchHistorySettingsComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
