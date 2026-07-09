import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { QueryModel } from '@app/models';
import { TotalResults } from '@app/models/total-results';
import { SearchService } from '@app/services';
import { SimpleStore } from '@app/store/simple-store';

@Component({
    selector: '[ia-results-count]',
    standalone: false,
    templateUrl: './results-count.component.html',
    styleUrl: './results-count.component.scss'
})
export class ResultsCountComponent implements OnChanges {
    @Input({required: true }) queryModel: QueryModel;

    totalResults: TotalResults;

    constructor(
        private searchService: SearchService,
    ) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.queryModel) {
            this.totalResults?.complete();
            this.totalResults = new TotalResults(
                new SimpleStore(), this.searchService, this.queryModel
            );
        }
    }
}
