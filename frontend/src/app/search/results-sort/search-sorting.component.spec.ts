import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { corpusFactory } from '@mock-data/corpus';
import { commonTestBed } from '@app/common-test-bed';
import { QueryModel } from '@models';

import { SearchSortingComponent } from './search-sorting.component';
import { PageResults } from '@models/page-results';
import { SimpleStore } from '@app/store/simple-store';
import { SearchServiceMock } from '@mock-data/search';
import { SearchService } from '@services';


describe('Search Sorting Component', () => {
    let component: SearchSortingComponent;
    let fixture: ComponentFixture<SearchSortingComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(SearchSortingComponent);
        component = fixture.componentInstance;
        component.pageResults = new PageResults(
            new SimpleStore(),
            new SearchServiceMock() as unknown as SearchService,
            new QueryModel(corpusFactory()),
        );
        fixture.detectChanges();
    });

    it('should be created', () => {
        expect(component).toBeTruthy();
    });
});

