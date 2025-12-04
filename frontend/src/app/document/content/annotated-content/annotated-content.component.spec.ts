import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AnnotatedContentComponent } from './annotated-content.component';

describe('AnnotatedContentComponent', () => {
  let component: AnnotatedContentComponent;
  let fixture: ComponentFixture<AnnotatedContentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AnnotatedContentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AnnotatedContentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
