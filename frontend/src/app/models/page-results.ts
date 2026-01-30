import { Observable, combineLatest, from, of } from 'rxjs';
import { QueryModel } from './query';
import { map } from 'rxjs/operators';
import { SearchService } from '@services';
import { SearchResults } from './search-results';
import { Results } from './results';
import { DocumentPage } from './document-page';
import { SortBy, SortDirection, SortState } from './sort';
import { Params } from '@angular/router';
import { Store } from '../store/types';
import {
    pageResultsParametersFromParams,
    pageResultsParametersToParams,
} from '@utils/params';

export const RESULTS_PER_PAGE = 20;
export const DEFAULT_HIGHLIGHT_SIZE = 200;

export interface PageParameters {
    from: number;
    size: number;
}

export type PageResultsParameters =  {
    sort: SortState;
    highlight?: number;
} & PageParameters;

const resultsToPage = (results: SearchResults, from: number): DocumentPage =>
    new DocumentPage(results.documents, results.total.value, results.fields, from);

export class PageResults extends Results<PageResultsParameters, DocumentPage> {
    sort$: Observable<SortState>;
    highlight$: Observable<number|undefined>;
    from$: Observable<number>;
    to$: Observable<number>;

    size = RESULTS_PER_PAGE;

    constructor(
        store: Store,
        private searchService: SearchService,
        query: QueryModel,
    ) {
        super(store, query, ['sort', 'highlight', 'p']);
        this.connectToStore();
        this.getResults();
        this.sort$ = this.state$.pipe(map(params => params.sort));
        this.highlight$ = this.state$.pipe(map(params => params.highlight));
        this.from$ = this.state$.pipe(
            map(parameters => parameters.from + 1)
        );
        this.to$ = combineLatest([this.state$, this.result$]).pipe(
            map(this.highestDocumentIndex)
        );
    }

    get highlightDisabled(): boolean {
        return !this.query.queryText;
    }

    /** Parameters to re-assign when the query model is updated. */
    assignOnQueryUpdate(): Partial<PageResultsParameters> {
        if (this.highlightDisabled) {
            return {
                highlight: undefined,
                from: 0
            };
        } else {
            return {
                from: 0
            };
        }
    }

    fetch(params: PageResultsParameters): Observable<DocumentPage> {
        return from(this.searchService.loadResults(
            this.query, params
        )).pipe(
            map(results => resultsToPage(results, params.from))
        );
    }

    /**
     * change the field by which results are sorted, and reset the sort direction and page
     */
    setSortBy(value: SortBy) {
        // check if the new value is actually different to avoid resetting the direction
        // for nothing
        const currentValue = this.state$.value.sort[0];
        if (value?.name !== currentValue?.name) {
            this.setParams({
                sort: [value, 'desc'],
                from: 0,
            });
        }
    }

    /** change the sort direction and reset the page */
    setSortDirection(value: SortDirection) {
        const [sortBy, _] = this.state$.value.sort;
        this.setParams({
            sort: [sortBy, value],
            from: 0,
        });
    }

    protected stateToStore(state: PageResultsParameters): Params {
        return pageResultsParametersToParams(state, this.query.corpus);
    }

    protected storeToState(params: Params): PageResultsParameters {
        return pageResultsParametersFromParams(params, this.query.corpus);
    }

    private highestDocumentIndex([parameters, result]: [PageResultsParameters, DocumentPage]): number {
        const limit = parameters.from + parameters.size;
        return Math.min(limit, result.total);
    }

}
