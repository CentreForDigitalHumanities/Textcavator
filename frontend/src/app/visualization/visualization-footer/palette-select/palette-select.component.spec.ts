import { ComponentFixture, TestBed } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { PaletteSelectComponent } from './palette-select.component';

describe('PaletteSelectComponent', () => {
    let component: PaletteSelectComponent;
    let fixture: ComponentFixture<PaletteSelectComponent>;

  beforeEach(async () => {
    commonTestBed().testingModule.compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PaletteSelectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
