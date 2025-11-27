import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { TermComparisonEditorComponent } from './term-comparison-editor.component';

describe('TermComparisonEditorComponent', () => {
  let component: TermComparisonEditorComponent;
  let fixture: ComponentFixture<TermComparisonEditorComponent>;

  beforeEach(waitForAsync(() => {
    commonTestBed().testingModule.compileComponents();
}));

  beforeEach(() => {
    fixture = TestBed.createComponent(TermComparisonEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
