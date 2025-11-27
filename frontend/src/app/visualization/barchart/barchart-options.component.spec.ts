import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { commonTestBed } from '@app/common-test-bed';

import { BarchartOptionsComponent } from './barchart-options.component';

describe('BarchartOptionsComponent', () => {
  let component: BarchartOptionsComponent;
  let fixture: ComponentFixture<BarchartOptionsComponent>;

  beforeEach(waitForAsync(() => {
      commonTestBed().testingModule.compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BarchartOptionsComponent);
    component = fixture.componentInstance;
    component.queryText = 'spam';
    component.showTokenCountOption = true;
    component.isLoading = true;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
