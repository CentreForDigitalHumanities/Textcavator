import { booleanFieldFactory, dateFieldFactory, keywordFieldFactory } from '@mock-data/corpus';
import { BooleanFilter, DateFilter, DateFilterData, MultipleChoiceFilter } from './field-filter';
import { SimpleStore } from '../store/simple-store';
import { Store } from '../store/types';

describe('SearchFilter', () => {
    // while these tests are ran on the DateFilter,
    // they test logic implemented in the abstract
    // SearchFilter class

    const field = dateFieldFactory();
    let store: Store;
    let filter: DateFilter;
    const exampleData: DateFilterData = {
        min: new Date(Date.parse('Jan 01 1850')),
        max: new Date(Date.parse('Dec 31 1860'))
    };
    const isActive = () => filter.state$.value.active;

    beforeEach(() => {
        store = new SimpleStore();
        filter = new DateFilter(store, field);
    });

    it('should toggle', () => {
        expect(isActive()).toBeFalse();

        // set some non-default data so the filter will not reject activation
        filter.set(exampleData);
        expect(isActive()).toBeTrue();

        filter.toggle();
        expect(isActive()).toBeFalse();
        filter.toggle();
        expect(isActive()).toBeTrue();

        filter.deactivate();
        expect(isActive()).toBeFalse();
        filter.activate();
        expect(isActive()).toBeTrue();
        filter.activate();
        expect(isActive()).toBeTrue();
    });

    it('should activate when value is set to non-default', () => {
        expect(isActive()).toBeFalse();

        filter.set(filter.defaultData);
        expect(isActive()).toBeFalse();

        filter.set(exampleData);
        expect(isActive()).toBeTrue();
    });

    it('should deactivate when reset', () => {
        filter.set(exampleData);
        expect(isActive()).toBeTrue();

        filter.reset();
        expect(isActive()).toBeFalse();
    });

    it('should be resettable when activated', () => {
        filter.set(exampleData);

        expect(filter.state$.value).toEqual({
            active: true,
            data: exampleData
        });

        filter.reset();

        expect(filter.state$.value).toEqual({
            active: false,
            data: filter.defaultData
        });

    });

    it('should be resettable when deactivated', () => {
        filter.set(exampleData);
        filter.deactivate();

        expect(filter.state$.value).toEqual({
            active: false,
            data: exampleData
        });

        filter.reset();

        expect(filter.state$.value).toEqual({
            active: false,
            data: filter.defaultData
        });
    });

    it('should ignore activation without data', () => {
        expect(isActive()).toBeFalse();

        filter.activate();
        expect(isActive()).toBeFalse();

        filter.toggle();
        expect(isActive()).toBeFalse();
    });

    it('should set from parameters', () => {
        store.paramUpdates$.next({
            date: '1850-01-01:1860-01-01'
        });

        expect(isActive()).toBeTrue();

        store.paramUpdates$.next({
            date: null,
        });

        expect(isActive()).toBeFalse();
    });
});

describe('DateFilter', () => {
    const field = dateFieldFactory();
    let filter: DateFilter;
    const exampleData = {
        min: new Date(Date.parse('Jan 01 1850')),
        max: new Date(Date.parse('Dec 31 1860'))
    };

    beforeEach(() => {
        const store = new SimpleStore();
        filter = new DateFilter(store, field);
    });

    it('should create', () => {
        expect(filter).toBeTruthy();
        expect(filter.currentData).toEqual(filter.defaultData);
        expect(filter.currentData).toEqual({
            min: new Date(Date.parse('Jan 01 1800')),
            max: new Date(Date.parse('Dec 31 1899'))
        });
    });

    it('should convert from and to string', () => {
        expect(filter.dataFromString(filter.dataToString(filter.currentData)))
            .toEqual(filter.currentData);
    });

    it('should set data from a value', () => {
        const date = new Date(Date.parse('Jan 01 1850'));
        filter.setToValue(date);
        expect(filter.currentData).toEqual({
            min: date,
            max: date,
        });
    });

    it('should convert to an elasticsearch filter', () => {
        filter.set(exampleData);
        const esFilter = filter.toEsFilter();
        expect(esFilter).toEqual({
            range: {
                date: {
                    gte: '1850-01-01',
                    lte: '1860-12-31',
                    format: 'yyyy-MM-dd',
                    relation: 'within',
                }
            }
        });
    });

    it('should parse an elasticsearch filter', () => {
        filter.set(exampleData);
        const esFilter = filter.toEsFilter();
        expect(filter.dataFromEsFilter(esFilter)).toEqual(filter.currentData);
    });
});

describe('MultipleChoiceFilter', () => {
    const field = keywordFieldFactory();
    let filter: MultipleChoiceFilter;
    const exampleData = ['test'];

    beforeEach(() => {
        const store = new SimpleStore();
        filter = new MultipleChoiceFilter(store, field);
    });

    it('should create', () => {
        expect(filter).toBeTruthy();
        expect(filter.currentData).toEqual(filter.defaultData);
        expect(filter.currentData).toEqual([]);
    });

    it('should convert to a string', () => {
        expect(filter.dataFromString(filter.dataToString(filter.currentData)))
            .toEqual(filter.currentData);

        // non-empty value
        filter.set(['a', 'b', 'value with spaces']);
        expect(filter.dataFromString(filter.dataToString(filter.currentData)))
            .toEqual(filter.currentData);
    });

    it('should convert values to valid URI components', () => {
        filter.set(['a long value']);
        expect(filter.dataToString(filter.currentData)).not.toContain(' ');
    });

    it('should set data from a value', () => {
        const value = 'a great value';
        filter.setToValue(value);
        expect(filter.currentData).toEqual([value]);
    });

    it('should convert to an elasticsearch filter', () => {
        filter.set(['wow!', 'a great selection!']);
        const esFilter = filter.toEsFilter();
        expect(esFilter).toEqual({
            terms: {
                genre: ['wow!', 'a great selection!']
            }
        });
    });

    it('should parse an elasticsearch filter', () => {
        filter.set(exampleData);
        const esFilter = filter.toEsFilter();
        expect(filter.dataFromEsFilter(esFilter)).toEqual(filter.currentData);
    });
});

describe('BooleanFilter', () => {
    const field = booleanFieldFactory();
    let store: SimpleStore;
    let filter: BooleanFilter;

    beforeEach(() => {
        store = new SimpleStore();
        filter = new BooleanFilter(store, field);
    });

    it('should set', () => {
        const checkData = (data: boolean) => expect(filter.state$.value.data).toBe(data);

        checkData(undefined);

        filter.set(true);
        checkData(true);

        filter.set(false);
        checkData(false);
    });
});
