import _ from "lodash";
import { BehaviorSubject, combineLatest, filter, map, Observable, shareReplay, tap, withLatestFrom } from "rxjs";

export class TablePaginator<Row extends object> {
    data$: BehaviorSubject<Row[]>;
    page$ = new BehaviorSubject<number>(1);
    sort$ = new BehaviorSubject<string | null>(null);

    totalSize$: Observable<number>;
    pageData$: Observable<Row[]>;

    private sortedData$: Observable<Row[]>;

    constructor(data: Row[], public pageSize: number = 10) {
        this.data$ = new BehaviorSubject<Row[]>(data);
        this.totalSize$ = this.data$.pipe(
            filter(data => !_.isUndefined(data)),
            map(data => data.length)
        )  ;
        this.sortedData$ = combineLatest([this.data$, this.sort$]).pipe(
            filter(([data, sort]) => !_.isUndefined(data)),
            map(([data, sort]) => sort ? _.sortBy(data, sort) : data),
            shareReplay(1), // replay as sorting may be expensive
        );
        this.pageData$ = combineLatest([this.sortedData$, this.page$]).pipe(
            map(([data, page]) => this.slicePage(data, page)),
        );
    }

    slicePage(data: Row[], page: number): Row[] {
        const start = (page - 1) * this.pageSize;
        const end = page * this.pageSize;
        return data.slice(start, end);
    }
}
