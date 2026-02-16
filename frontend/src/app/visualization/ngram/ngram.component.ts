import { Component, ElementRef, EventEmitter, HostBinding, Input, OnChanges, Output, SimpleChanges, ViewChild } from '@angular/core';
import * as _ from 'lodash';
import { Subject } from 'rxjs';

import { formIcons } from '@shared/icons';
import {
    Corpus,
    FreqTableHeaders,
    QueryModel,
    CorpusField,
    NgramResults,
    SuccessfulTask,
} from '@models';
import {
    ApiService,
    NotificationService,
    VisualizationService,
} from '@services';

import { RouterStoreService } from '@app/store/router-store.service';
import { NgramParameters, NgramSettings } from '@models/ngram';


@Component({
    selector: 'ia-ngram',
    templateUrl: './ngram.component.html',
    styleUrls: ['./ngram.component.scss'],
    standalone: false
})
export class NgramComponent implements OnChanges {
    @HostBinding('style.display') display = 'block'; // needed for loading spinner positioning

    @Input() queryModel: QueryModel;
    @Input() corpus: Corpus;
    @Input() visualizedField: CorpusField;
    @Input() asTable: boolean;
    @Input() palette: string[];

    @Output() ngramError = new EventEmitter<string>();

    @ViewChild('chart-container') chartContainer: ElementRef;

    keysInStore = ['ngramSettings'];

    allDateFields: CorpusField[];
    dateField: CorpusField;

    stopPolling$ = new Subject<void>();

    tableHeaders: FreqTableHeaders = [
        { key: 'date', label: 'Date', isMainFactor: true },
        { key: 'ngram', label: 'N-gram', isSecondaryFactor: true },
        {
            key: 'freq',
            label: 'Frequency',
            format: this.formatValue,
            formatDownload: this.formatDownloadValue,
        },
    ];
    tableData: { date: string; ngram: string; freq: number }[];

    currentResults: NgramResults;

    // options
    modeOptions = [
        { label: 'ngrams', value: 'ngrams' },
        { label: 'collocates', value: 'collocates' },
    ];
    sizeOptions = [
        { label: 'bigrams', value: 2 },
        { label: 'trigrams', value: 3 },
        { label: 'fourgrams', value: 4 },
    ];
    positionsOptions = ['any', 'first', 'second'].map((n) => ({
        label: `${n}`,
        value: n,
    }));
    freqCompensationOptions = [
        { label: 'No', value: false },
        { label: 'Yes', value: true },
    ];
    analysisOptions: { label: string; value: string }[];
    maxDocumentsOptions = [50, 100, 200, 500].map((n) => ({
        label: `${n}`,
        value: n,
    }));
    numberOfNgramsOptions = [10, 20, 50, 100].map((n) => ({
        label: `${n}`,
        value: n,
    }));

    tasksToCancel: string[];

    resultsCache: { [parameters: string]: any } = {};
    ngramParameters: NgramParameters;
    currentSettings: NgramSettings;
    parametersChanged = false;
    dataHasLoaded: boolean;
    isLoading = false;

    formIcons = formIcons;

    nullableParameters = ['ngramSettings'];

    constructor(
        private apiService: ApiService,
        private visualizationService: VisualizationService,
        private notificationService: NotificationService,
        store: RouterStoreService,
    ) {
        this.ngramParameters = new NgramParameters(
            store,
        );
        this.currentSettings = _.clone(this.ngramParameters.state$.value);
    }

    get currentModeOption() {
        return this.modeOptions.find(
            (item) => item.value === this.currentSettings.mode
        );
    }

    get currentSizeOption() {
        return this.sizeOptions.find(
            (item) => item.value === this.currentSettings.size
        );
    }

    get currentPositionsOption() {
        return this.positionsOptions.find(
            (item) => item.value === this.currentSettings.positions
        );
    }

    get currentFreqCompensationOption() {
        return this.freqCompensationOptions.find(
            (item) => item.value === this.currentSettings.freqCompensation
        );
    }

    get currentAnalysisOption() {
        return this.analysisOptions.find(
            (item) => item.value === this.currentSettings.analysis
        );
    }

    get currentMaxDocumentsOption() {
        return this.maxDocumentsOptions.find(
            (item) => item.value === this.currentSettings.maxDocuments
        );
    }

    get currentNumberOfNgramsOption() {
        return this.numberOfNgramsOptions.find(
            (item) => item.value === this.currentSettings.numberOfNgrams
        );
    }

    ngOnDestroy(): void {
        this.stopPolling$.next();
        this.ngramParameters.complete();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.corpus) {
            this.allDateFields = this.corpus.fields.filter(
                (field) => field.mappingType === 'date'
            );
            this.dateField = this.allDateFields[0];
        }
        if (changes.queryModel || changes.visualizedField) {
            this.resultsCache = {};
            if (this.visualizedField.multiFields) {
                this.analysisOptions = [
                    { label: 'None', value: 'none' },
                ].concat(
                    this.visualizedField.multiFields.map((subfield) => {
                        const displayStrings = {
                            clean: 'Remove stopwords',
                            stemmed: 'Stem and remove stopwords',
                        };
                        return {
                            value: subfield,
                            label: displayStrings[subfield],
                        };
                    })
                );
            } else {
                this.analysisOptions = undefined;
            }
        }

        if (this.ngramParameters.state$.value) {
            this.loadGraph();
        }

    }

    loadGraph() {
        this.isLoading = true;
        this.dataHasLoaded = false;
        const cachedResult = this.getCachedResult();

        if (cachedResult) {
            this.onDataLoaded(cachedResult);
        } else {
            this.visualizationService.getNgramTasks(
                this.queryModel, this.corpus, this.visualizedField.name,
                this.currentSettings, this.dateField.name).then(
                    response => {
                        this.tasksToCancel = response.task_ids;
                        // tasksToCancel contains ids of the parent task and its subtasks
                        // we are only interested in the outcome of the parent task (first in array)
                        const poller$ = this.apiService.pollTasks([this.tasksToCancel[0]], this.stopPolling$);
                        poller$.subscribe({
                            error: (error) => this.onFailure(error),
                            next: (result: SuccessfulTask<NgramResults[]>) => this.onDataLoaded((result).results[0]),
                            complete: () => {
                                if (!this.dataHasLoaded) {
                                    this.apiService.abortTasks({ task_ids: this.tasksToCancel });
                                    this.tasksToCancel = null;
                                }
                            }
                    });
            });
        }
    }

    onFailure(error: {message: string}) {
        console.error(error);
        this.currentResults = undefined;
        this.ngramError.emit(error.message);
        this.isLoading = false;
    }

    onDataLoaded(result: NgramResults) {
        this.dataHasLoaded = true;
        this.currentResults = result;
        this.cacheResult(result);
        this.tableData = this.makeTableData(result);
        this.isLoading = false;
    }

    makeTableData(result: NgramResults): typeof this.tableData {
        return _.flatMap(
            result.time_points.map((date, index) =>
                result.words.map((dataset) => ({
                    date,
                    ngram: dataset.label,
                    freq: dataset.data[index],
                }))
            )
        );
    }

    cacheResult(result: any): void {
        const key = this.concatenateDateField(this.ngramParameters.stringifyNgramSettings(this.currentSettings));
        if (key) {
            this.resultsCache[key] = result;
        }
    }

    getCachedResult(): any {
        const key = this.concatenateDateField(this.ngramParameters.stringifyNgramSettings(this.currentSettings));
        if (key && _.has(this.resultsCache, key)) {
            return this.resultsCache[key];
        }
    }

    concatenateDateField(key: string): string {
        // add the date field to the resultsCache key: it is currently not handled by ngramParameters
        // TO DO: this is a workaround, remove if ngramParameters are implemented to handle date field
        if (this.allDateFields.length) {
            key.concat(`f:${this.dateField.name}`)
        }
        return key
    }

    setPositionsOptions(size) {
        // set positions dropdown options and reset its value
        this.positionsOptions = ['any']
            .concat(['first', 'second', 'third', 'fourth'].slice(0, size))
            .map((item) => ({ value: item, label: item }));
    }

    onParameterChange(parameter: string, value: any) {
        if (_.get(this.currentSettings, parameter) === value) {
            return;
        }
        _.assign(this.currentSettings, {[parameter]: value});

        if (parameter === 'size' && value) {
            this.setPositionsOptions(value);
        }

        this.parametersChanged = true;
        this.stopPolling$.next();
    }

    cancelChanges() {
        this.parametersChanged = false;
    }

    confirmChanges() {
        this.ngramParameters.setParams(this.currentSettings);
        this.isLoading = true;
        this.parametersChanged = false;
        this.loadGraph();
    }

    formatValue(value: number): string {
        if (value === 0) {
            return '0';
        }

        return `${value.toPrecision(3)}`;
    }

    formatDownloadValue(value: number): string {
        if (value === 0) {
            return '0';
        }

        return `${value}`;
    }

    requestFullData() {
        const parameters = this.visualizationService.makeNgramRequestParameters(
            this.corpus,
            this.queryModel,
            this.visualizedField.name,
            this.ngramParameters.state$.value,
            this.dateField.name
        );
        this.apiService
            .requestFullData({
                corpus_name: this.corpus.name,
                visualization: 'ngram',
                parameters,
            })
            .then(() =>
                this.notificationService.showMessage(
                    'Full data requested! You will receive an email when your download is ready.',
                    'success',
                    {
                        text: 'view downloads',
                        route: ['/download-history'],
                    }
                )
            )
            .catch((error) => {
                console.error(error);
                this.notificationService.showMessage(
                    'Could not set up data generation.',
                    'danger'
                );
            });
    }
}
