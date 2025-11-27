import { ComponentFixture, TestBed } from '@angular/core/testing';
import { corpusFactory } from '@mock-data/corpus';
import { commonTestBed } from '@app/common-test-bed';
import { QueryModel } from '@models';

import { HighlightSelectorComponent } from './highlight-selector.component';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';
import { PageResults } from '@models/page-results';
import { SimpleStore } from '@app/store/simple-store';
import { SearchServiceMock } from '@mock-data/search';
import { SearchService } from '@services';

describe('HighlightSelectorComponent', () => {
    let component: HighlightSelectorComponent;
    let fixture: ComponentFixture<HighlightSelectorComponent>;

    beforeEach(async () => {
        commonTestBed().testingModule.compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(HighlightSelectorComponent);
        component = fixture.componentInstance;
        component.pageResults = new PageResults(
            new SimpleStore(),
            new SearchServiceMock() as any as SearchService,
            new QueryModel(corpusFactory())
        );
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should reflect the results model state', () => {
        const button = fixture.debugElement.query(By.css('#highlight-toggle'));

        const innerText = (el: DebugElement) => el.nativeElement.innerText;

        expect(innerText(button)).toBe('OFF');

        component.pageResults.setParams({highlight: 200});
        fixture.detectChanges();

        expect(innerText(button)).toBe('ON');
    });
});
