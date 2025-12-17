import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { SelectFieldComponent } from './select-field.component';
import { commonTestBed } from '@app/common-test-bed';
import { corpusFactory } from '@mock-data/corpus';
import { QueryModel } from '@models';

describe('SelectFieldComponent', () => {
  let component: SelectFieldComponent;
  let fixture: ComponentFixture<SelectFieldComponent>;

  beforeEach(waitForAsync(() => {
    commonTestBed().testingModule.compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SelectFieldComponent);
    component = fixture.componentInstance;
    component.queryModel = new QueryModel(corpusFactory());
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
