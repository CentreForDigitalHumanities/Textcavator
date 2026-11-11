import { Component, OnDestroy, OnInit } from '@angular/core';

import { RangeFilterData, RangeFilter, QueryModel } from '@models';
import { BaseFilterComponent } from '../base-filter.component';
import { Subject, interval } from 'rxjs';
import { debounce, takeUntil } from 'rxjs/operators';
import { Aggregator, MaxAggregator, MinAggregator } from '@models/aggregation';
import { SearchService } from '@services';
import * as _ from 'lodash';

@Component({
    selector: 'ia-range-filter',
    templateUrl: './range-filter.component.html',
    styleUrls: ['./range-filter.component.scss'],
    standalone: false
})
export class RangeFilterComponent extends BaseFilterComponent<RangeFilter> implements OnInit, OnDestroy {
    min: number;
    max: number;

    sliderValue$ = new Subject<[number, number]>();

    private destroy$ = new Subject<void>();

    constructor(private searchService: SearchService) {
        super();
    }

    ngOnInit(): void {
        this.sliderValue$.pipe(
            takeUntil(this.destroy$),
            debounce(() => interval(300))
        ).subscribe(value =>
            this.update(this.getFilterData(value))
        );
    }

    ngOnDestroy(): void {
        this.destroy$.next(undefined);
        this.destroy$.complete();
    }

    onFilterSet(filter: RangeFilter): void {
        this.fetchDefaultData(filter).then(data =>
            filter.setDefaultData(data)
        ).then(() => {
            this.min = filter.defaultData.min;
            this.max = filter.defaultData.max;
        });
    }

    getFilterData(value: [number, number]): RangeFilterData {
        return {
            min: value[0],
            max: value[1],
        };
    }

    /** Calculate step size based on min/max.
     * Returns the power of 10 for which there are [100, 1000) steps.
     * If the field is an integer field, the step is always at least 1.
     */
    step(min: number, max: number): number {
        const minStep = this.filter.corpusField.mappingType == 'integer' ? 1 : 0;
        const range = max - min;
        // Express the range as a power of 10, round down to the nearest integer,
        // subtract 2, then raise 10 by that amount.
        // E.g. 1547 -> 3.19... -> 3 -> 1 -> 10.
        const idealStepSize = 10 ** (Math.floor(Math.log10(range)) - 2);
        return Math.max(idealStepSize, minStep);
    }

    private fetchDefaultData(filter: RangeFilter): Promise<RangeFilterData> {
        return Promise.all(
            [this.fetchMin(filter), this.fetchMax(filter)]
        ).then(([min, max]) => ({min, max}));
    }

    private fetchMin(filter: RangeFilter): Promise<number> {
        if (!_.isUndefined(filter.defaultData.min)) {
            return Promise.resolve(filter.defaultData.min);
        }
        return this.fetchAggregation(new MinAggregator(filter.corpusField));
    }

    private fetchMax(filter: RangeFilter): Promise<number> {
        if (!_.isUndefined(filter.defaultData.max)) {
            return Promise.resolve(filter.defaultData.max);
        }
        return this.fetchAggregation(new MaxAggregator(filter.corpusField));
    }

    private fetchAggregation<Result>(aggregator: Aggregator<Result>): Promise<Result> {
        const queryModel = new QueryModel(this.queryModel.corpus);
        return this.searchService.aggregateSearch(
            queryModel.corpus, queryModel, aggregator
        );
    }
}
