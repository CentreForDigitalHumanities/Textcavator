import { Component } from '@angular/core';

import * as _ from 'lodash';

import { TermsAggregator, TermsResult } from '@models/aggregation';
import { SearchService } from '@services';
import { MultipleChoiceFilter, MultipleChoiceFilterOptions } from '@models';
import { BaseFilterComponent } from '../base-filter.component';
import { MultiSelectLazyLoadEvent } from 'primeng/multiselect';

@Component({
    selector: 'ia-multiple-choice-filter',
    templateUrl: './multiple-choice-filter.component.html',
    styleUrls: ['./multiple-choice-filter.component.scss'],
    standalone: false
})
export class MultipleChoiceFilterComponent extends BaseFilterComponent<MultipleChoiceFilter> {
    options: { label: string; value: string; doc_count: number }[] = [];
    allOptionsCalled: boolean = false;

    constructor(private searchService: SearchService) {
        super();
    }

    onFilterSet(): void {
        this.getOptions();
    }

    onQueryModelUpdate(): void {
        if( this.allOptionsCalled ) {
            this.getOptions(true);
        }
        this.getOptions(false);
    }

    /** Gets all the filter options from ES, only if there are more than 10 options for that filter */
    getAllOptionsFromES(event:MultiSelectLazyLoadEvent) {
        const optionCount = (this.filter.corpusField.filterOptions as MultipleChoiceFilterOptions).option_count;
        if (optionCount > 10) {
            this.getOptions(true);
            this.allOptionsCalled = true;
        }
    }

    private async getOptions(all: boolean = false): Promise<void> {
        if (this.filter && this.queryModel) {
            // optionCount is set to the maximum when the filter panel is shown, but not when other filters change
            const optionCount = all ? 10000 : (this.filter.corpusField.filterOptions as MultipleChoiceFilterOptions).option_count;
            const aggregator = new TermsAggregator(this.filter.corpusField, optionCount);
            const queryModel = this.queryModel.clone();
            queryModel.filterForField(this.filter.corpusField).deactivate();

            const parseOption = (item: TermsResult) => ({
                label: item.key, value: item.key, doc_count: item.doc_count
            });
            this.searchService.aggregateSearch(
                queryModel.corpus, queryModel, aggregator
            ).then(result =>
                this.options = _.sortBy(result.map(parseOption), option => option.label)
            ).catch(() =>
                this.options = []
            );
        }
    }
}
