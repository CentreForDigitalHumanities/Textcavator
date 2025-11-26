import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { WordSimilarityComponent } from './word-similarity.component';

describe('WordSimilarityComponent', () => {
    let component: WordSimilarityComponent;
    let fixture: ComponentFixture<WordSimilarityComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(WordSimilarityComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
