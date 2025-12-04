import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HighlightedContentComponent } from './highlighted-content.component';

describe('HighlightedContentComponent', () => {
  let component: HighlightedContentComponent;
  let fixture: ComponentFixture<HighlightedContentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HighlightedContentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HighlightedContentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
