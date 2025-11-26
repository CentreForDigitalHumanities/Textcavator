import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { DownloadHistoryComponent } from './download-history.component';

describe('DownloadHistoryComponent', () => {
    let component: DownloadHistoryComponent;
    let fixture: ComponentFixture<DownloadHistoryComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DownloadHistoryComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
