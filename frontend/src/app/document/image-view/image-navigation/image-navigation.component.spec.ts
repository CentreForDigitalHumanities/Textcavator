import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { ImageNavigationComponent } from './image-navigation.component';

describe('ImageNavigationComponent', () => {
  let component: ImageNavigationComponent;
  let fixture: ComponentFixture<ImageNavigationComponent>;

  beforeEach(waitForAsync(() => {
    commonTestBed().testingModule.compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ImageNavigationComponent);
    component = fixture.componentInstance;
    component.pageIndices = [40,41,42,43,44];
    component.initialPage = 42;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
