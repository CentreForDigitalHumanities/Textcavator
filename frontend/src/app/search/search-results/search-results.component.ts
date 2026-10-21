/* eslint-disable @typescript-eslint/member-ordering */
import {
    Component,
    Input,
    OnChanges,
    OnDestroy,
    SimpleChanges,
} from '@angular/core';

import { Observable, Subject, map, takeUntil } from 'rxjs';
import { ErrorDetails } from '@shared/error/error.component';
import { QueryModel, SearchResults, User } from '@models/index';
import { PageResults, PageResultsParameters } from '@models/page-results';
import { SearchService } from '@services';
import { RouterStoreService } from '@app/store/router-store.service';

const MAXIMUM_DISPLAYED = 10000;

@Component({
    selector: 'ia-search-results',
    templateUrl: './search-results.component.html',
    styleUrls: ['./search-results.component.scss'],
    standalone: false
})
export class SearchResultsComponent implements OnChanges, OnDestroy {
    /**
     * The search queryModel to use
     */
    @Input()
    public queryModel: QueryModel;

    @Input()
    public user: User;

    public pageResults: PageResults;
    public isLoading = false;
    public results: SearchResults;

    public resultsPerPage = 20;

    error$: Observable<ErrorDetails>;

    /** tab on which the focused document should be opened */
    public documentTabIndex: number;

    private destroy$ = new Subject<void>();

    constructor(
        private routerStoreService: RouterStoreService,
        private searchService: SearchService,
    ) { }

    ngOnChanges(changes: SimpleChanges) {
        if (changes.queryModel) {
            this.pageResults?.complete();
            this.pageResults = new PageResults(
                this.routerStoreService,
                this.searchService,
                this.queryModel
            );
            this.error$ = this.pageResults.error$.pipe(map(this.parseError));
            this.pageResults.result$
                .pipe(takeUntil(this.destroy$))
                .subscribe();
        }
    }

    ngOnDestroy(): void {
        this.pageResults?.complete();
        this.destroy$.next(undefined);
        this.destroy$.complete();
    }

    setParameters(parameters: PageResultsParameters) {
        this.pageResults?.setParams(parameters);
    }

    totalDisplayed(totalResults: number) {
        return Math.min(totalResults, MAXIMUM_DISPLAYED);
    }

    private parseError(error): ErrorDetails {
        if (error) {
            return {
                date: new Date().toISOString(),
                href: location.href,
                message: error.message || 'An unknown error occurred',
            };
        }
    }
}
