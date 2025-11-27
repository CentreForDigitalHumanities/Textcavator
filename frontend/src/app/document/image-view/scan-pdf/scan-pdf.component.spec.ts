import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { commonTestBed } from '@app/common-test-bed';

import { ScanPdfComponent } from './scan-pdf.component';

describe('ScanPdfComponent', () => {
  let component: ScanPdfComponent;
  let fixture: ComponentFixture<ScanPdfComponent>;

  beforeEach(waitForAsync(() => {
    commonTestBed().testingModule.compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScanPdfComponent);
    component = fixture.componentInstance;
    component.imagePaths = ['super/awesome/image/path1.pdf'];
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
