import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { ScanImageComponent } from './scan-image.component';

describe('ScanImageComponent', () => {
  let component: ScanImageComponent;
  let fixture: ComponentFixture<ScanImageComponent>;

  beforeEach(waitForAsync(() => {
    commonTestBed().testingModule.compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScanImageComponent);
    component = fixture.componentInstance;
    component.imagePaths = ['https://image1.jpg', 'https://image2.jpg'];
    component.zoomFactor = 1.2;
    component.showPage = 1;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
