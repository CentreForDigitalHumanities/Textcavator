import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { DownloadOptionsComponent } from './download-options.component';

describe('DownloadOptionsComponent', () => {
    let component: DownloadOptionsComponent;
    let fixture: ComponentFixture<DownloadOptionsComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
      }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DownloadOptionsComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
