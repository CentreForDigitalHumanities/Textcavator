import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { WordcloudComponent, sizeScale } from './wordcloud.component';
import { commonTestBed } from '@app/common-test-bed';

describe('WordcloudComponent', () => {
  let component: WordcloudComponent;
  let fixture: ComponentFixture<WordcloudComponent>;

  beforeEach(waitForAsync(() => {
    commonTestBed().testingModule.compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(WordcloudComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});

describe('sizeScale', () => {
    it('should scale sizes', () => {
        const scale = sizeScale(100, 1000);
        expect(scale(100)).toBeCloseTo(10);
        expect(scale(1000)).toBeCloseTo(48);
    }
    );
});
