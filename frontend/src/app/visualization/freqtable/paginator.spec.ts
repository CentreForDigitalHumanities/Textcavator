import _ from "lodash";
import { TablePaginator } from "./paginator";

describe('TablePaginator', () => {
    let data: any[];
    let paginator: TablePaginator<any>;

    beforeEach(() => {
        data = _.range(100).map(i => ({ index: i, reverse: -i }));
        paginator = new TablePaginator(data, 10);
    });

    // note: the paginator itself does not use async scheduling so these tests can simply
    // subscribe to get observable values synchronously.

    it('stores data', () => {
        expect(paginator.data$.value).toEqual(data);

        let total = undefined;
        paginator.totalSize$.subscribe((value) => total = value);
        expect(total).toBe(100);
    });

    it('select page data', () => {
        let pageData = [];
        paginator.pageData$.subscribe((value) => pageData = value);
        expect(pageData.length).toBe(10);
        expect(pageData[0].index).toBe(0);
        expect(pageData[9].index).toBe(9);

        paginator.page$.next(2);
        expect(pageData[0].index).toBe(10);
        expect(pageData[9].index).toBe(19);
    });

    it('sorts data', () => {
        let pageData = [];
        paginator.pageData$.subscribe((value) => pageData = value);
        paginator.sortBy$.next('reverse');
        expect(pageData[0].index).toBe(99);
    });
});
