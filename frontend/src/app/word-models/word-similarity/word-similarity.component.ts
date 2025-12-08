import { Component, EventEmitter, HostBinding, Input, OnChanges, OnDestroy, Output, SimpleChanges } from '@angular/core';
import * as _ from 'lodash';
import { BehaviorSubject } from 'rxjs';
import { RouterStoreService } from '@app/store/router-store.service';
import { ComparedQueries } from '@models/compared-queries';
import { showLoading } from '@utils/utils';
import { Corpus, WordSimilarity } from '@models';
import { WordmodelsService } from '@services';

@Component({
    selector: 'ia-word-similarity',
    templateUrl: './word-similarity.component.html',
    styleUrls: ['./word-similarity.component.scss'],
    standalone: false
})
export class WordSimilarityComponent implements OnChanges, OnDestroy {
    @HostBinding('style.display') display = 'block'; // needed for loading spinner positioning

    @Input() corpus: Corpus;
    @Input() asTable: boolean;
    @Input() palette: string[];

    @Output() wordSimilarityError = new EventEmitter();

    isLoading$ = new BehaviorSubject<boolean>(false);

    comparisonTermLimit = Infinity;

    comparedQueries: ComparedQueries;

    results: WordSimilarity[][];
    timeIntervals: string[];

    data: WordSimilarity[];

    constructor(
        private wordModelsService: WordmodelsService,
        private routerStoreService: RouterStoreService) {
            this.comparedQueries = new ComparedQueries(this.routerStoreService);
            this.comparedQueries.allQueries$.subscribe(this.onTermsUpdate.bind(this))
        }

    @HostBinding('class.is-loading')
    get isLoading() {
        return this.isLoading$.value;
    }

    get queryText(): string {
        return this.comparedQueries.state$.value.primary;
    }

    get comparisonTerms(): string[] {
        return this.comparedQueries.state$.value.compare;
    }

    get tableFileName(): string {
        return `word similarity - ${this.queryText} - ${this.corpus?.title}`;
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (
            (changes.corpus) &&
            this.comparisonTerms.length
        ) {
            this.getData();
        } else {
            if (this.results) {
                this.onDataLoaded(this.results);
            }
        }
    }

    ngOnDestroy(): void {
        this.comparedQueries.complete();
    }

    onTermsUpdate() {
        if (this.corpus && this.comparisonTerms.length >= 1) {
            this.getData();
        } else {
            this.clearData();
        }
    }

    getData(): void {
        showLoading(
            this.isLoading$,
            Promise.all(
                this.comparisonTerms.map((term) =>
                    this.wordModelsService.getWordSimilarity(
                        this.queryText,
                        term,
                        this.corpus.name
                    )
                )
            )
        )
            .then(this.onDataLoaded.bind(this))
            .catch(this.onError.bind(this));
    }

    clearData() {
        this.results = undefined;
        this.timeIntervals = undefined;
        this.data = undefined;
    }

    getTimePoints(points: WordSimilarity[]) {
        return points.map((point) => point.time);
    }

    onDataLoaded(data: WordSimilarity[][]): void {
        this.results = data;
        this.timeIntervals =
            data.length && data[0].length
                ? this.getTimePoints(data[0])
                : this.timeIntervals;
        this.data = _.flatten(this.results);
    }

    onError(error: { message: string }) {
        this.results = undefined;
        this.wordSimilarityError.emit(error.message);
    }
}
