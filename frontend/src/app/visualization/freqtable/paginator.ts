import _ from "lodash";
import { BehaviorSubject, combineLatest, filter, map, Observable, shareReplay } from "rxjs";

export class TablePaginator<Row extends object> {
    data$: BehaviorSubject<Row[]>;
    page$ = new BehaviorSubject<number>(1);
    sortBy$ = new BehaviorSubject<string | null>(null);
    sortAscending$ = new BehaviorSubject<boolean>(true);

    totalSize$: Observable<number>;
    hasPages$: Observable<boolean>;
    pageData$: Observable<Row[]>;

    private sortedData$: Observable<Row[]>;

    constructor(data: Row[], public pageSize: number = 10) {
        this.data$ = new BehaviorSubject<Row[]>(data);
        this.totalSize$ = this.data$.pipe(
            filter(data => !_.isUndefined(data)),
            map(data => data?.length)
        );
        this.hasPages$ = this.totalSize$.pipe(
            map(size => size > this.pageSize),
        );
        this.sortedData$ = combineLatest([this.data$, this.sortBy$, this.sortAscending$]).pipe(
            filter(([data, sortBy, sortAsc]) => !_.isUndefined(data)),
            map(([data, sortBy, sortAsc]) => this.sort(data, sortBy, sortAsc)),
            shareReplay(1), // replay as sorting may be expensive
        );
        this.pageData$ = combineLatest([this.sortedData$, this.page$]).pipe(
            map(([data, page]) => this.slicePage(data, page)),
        );
    }

    toggleSort(key: string) {
        if (this.sortBy$.value === key) {
            this.sortAscending$.next(!this.sortAscending$.value);
        } else {
            this.sortBy$.next(key);
            this.sortAscending$.next(true);
        }
    }

    slicePage(data: Row[], page: number): Row[] {
        const start = (page - 1) * this.pageSize;
        const end = page * this.pageSize;
        return data.slice(start, end);
    }

    private sort(data: Row[], sortBy: string | null, ascending: boolean): Row[] {
        if (sortBy) {
            const sorted = _.sortBy(data, sortBy);
            if (ascending) {
                return sorted;
            } else {
                return sorted.reverse();
            }
        }
        return data;
    }
}
