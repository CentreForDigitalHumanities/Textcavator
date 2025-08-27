/* eslint-disable @typescript-eslint/member-ordering */
import { Directive, EventEmitter, Host, HostBinding, Input, OnChanges, OnDestroy, OnInit, Output, SimpleChanges } from '@angular/core';

import * as _ from 'lodash';

import {
    ApiService,
    NotificationService,
    SearchService,
} from '@services/index';
import { Chart, ChartOptions } from 'chart.js';
import {
    Corpus,
    FreqTableHeaders,
    QueryModel,
    CorpusField,
    TaskResult,
    BarchartSeries,
    TimelineDataPoint,
    HistogramDataPoint,
    TermFrequencyResult,
    ChartParameters,
} from '@models';
import Zoom from 'chartjs-plugin-zoom';
import { BehaviorSubject, Subject } from 'rxjs';
import { selectColor } from '@utils/select-color';
import { VisualizationService } from '@services/visualization.service';
import { showLoading } from '@utils/utils';
import { takeUntil } from 'rxjs/operators';
import { DateHistogramResult, TermsResult } from '@models/aggregation';
import { ComparedQueries } from '@models/compared-queries';
import { RouterStoreService } from '@app/store/router-store.service';

const hintSeenSessionStorageKey = 'hasSeenTimelineZoomingHint';
const hintHidingMinDelay = 500;       // milliseconds
const hintHidingDebounceTime = 1000;  // milliseconds
const barchartID = 'barchart';

@Directive({
    selector: 'ia-barchart',
    standalone: false
})

/** The barchartComponent is used to define shared functionality between the
 * histogram and timeline components. It does not function as a stand-alone component. */
export abstract class BarchartDirective<
    AggregateResult extends TermsResult | DateHistogramResult,
    DataPoint extends TimelineDataPoint | HistogramDataPoint
> implements OnChanges, OnInit, OnDestroy {
    @HostBinding('style.display') display = 'block'; // needed for loading spinner positioning

    public showHint: boolean;

    // rawData: a list of series
    rawData: BarchartSeries<DataPoint>[];

    // chart object
    chart: Chart;

    @Input() corpus: Corpus;
    @Input() queryModel: QueryModel;
    @Input() visualizedField: CorpusField;
    @Input() asTable: boolean;
    @Input() palette: string[];

    @Input() frequencyMeasure: 'documents' | 'tokens' = 'documents';

    normalizer: 'raw' | 'percent' | 'documents' | 'terms' = 'raw';
    chartType: 'bar' | 'line' | 'scatter' = 'bar';
    comparedQueries: ComparedQueries;

    documentLimit = 1000; // maximum number of documents to search through for term frequency
    documentLimitExceeded = false; // whether the results include documents than the limit
    totalTokenCountAvailable: boolean; // whether the data includes token count totals

    // table data
    tableHeaders: FreqTableHeaders;
    tableData: any[];


    /** Stores the key that can be used in a DataPoint object
     * to retrieve the y-axis value.
     * Key can be retrieved as
     * `valueKeys[frequencyMeasure][normalizer]`
     */
    valueKeys = {
        tokens: {
            raw: 'match_count',
            terms: 'matches_by_token_count',
            documents: 'matches_by_doc_count',
        },
        documents: {
            raw: 'doc_count',
            percent: 'relative_doc_count',
        },
    };

    isLoading$ = new BehaviorSubject<boolean>(false);

    // eslint-disable-next-line @angular-eslint/no-output-native
    @Output() error = new EventEmitter();

    destroy$ = new Subject<void>();
    stopPolling$ = new Subject<void>();

    tasksToCancel: string[];

    dataHasLoaded: boolean;

    basicChartOptions: ChartOptions = { // chart options not suitable for Chart.defaults.global
        scales: {
            x: {
                title: { display: true },
                border: { display: true },
                grid: { drawOnChartArea: false },
            },
            y: {
                type: 'linear',
                beginAtZero: true,
                title: { display: true, text: 'Frequency' },
                border: { display: true },
                grid: { drawOnChartArea: false },
                ticks: {
                    callback: (value, index, values) =>
                        this.formatValue(this.normalizer)(value as number),
                },
                min: 0,
            },
        },
        interaction: {
            axis: 'x',
        },
        plugins: {
            legend: {
                display: false,
            },
            zoom: {
                zoom: {
                    mode: 'x',
                    drag: {
                        enabled: true,
                        threshold: 0,
                    },
                    pinch: {
                        enabled: false,
                    },
                    wheel: {
                        enabled: false,
                    },
                    onZoom: ({ chart }) => this.onZoomIn(chart),
                },
            },
            title: {
                display: true,
                text: `placeholder`,
                align: 'center',
            },
        },
    };

    constructor(
        public searchService: SearchService,
        public visualizationService: VisualizationService,
        public apiService: ApiService,
        private notificationService: NotificationService,
        private routerStoreService: RouterStoreService,
    ) {
        const chartDefault = Chart.defaults;
        chartDefault.elements.bar.backgroundColor = selectColor();
        chartDefault.elements.bar.hoverBackgroundColor = selectColor();
        chartDefault.plugins.tooltip.displayColors = false;
        chartDefault.plugins.tooltip.intersect = false;
        this.comparedQueries = new ComparedQueries(this.routerStoreService);
        this.comparedQueries.allQueries$.subscribe(this.updateQueries.bind(this));
    }

    get isLoading() {
        return this.isLoading$.value;
    }

    ngOnInit(): void {
        this.setupZoomHint();
    }

    ngOnChanges(changes: SimpleChanges) {
        if (changes.queryModel) {
            this.queryModel.update
                .pipe(takeUntil(this.destroy$))
                .subscribe(this.refreshChart.bind(this));
        }
        // new doc counts should be requested if query has changed
        if (this.changesRequireRefresh(changes)) {
            this.refreshChart();
        } else if (changes.palette) {
            this.prepareChart();
        }
    }

    ngOnDestroy(): void {
        this.stopPolling$.next();
        this.destroy$.next(undefined);
        this.comparedQueries.complete();
    }

    /** check whether input changes should force reloading the data */
    changesRequireRefresh(changes: SimpleChanges): boolean {
        const relevantChanges = [
            changes.corpus,
            changes.queryModel,
            changes.visualizedField,
            changes.frequencyMeasure,
        ].filter((change) => !_.isUndefined(change));

        return _.some(
            relevantChanges,
            (change) => !_.isEqual(change.currentValue, change.previousValue)
        );
    }

    /** update graph after changes to the chart settings (i.e. normalizer and chart type) */
    onOptionChange(chartParameters: ChartParameters) {
        this.normalizer = chartParameters.normalizer;
        this.chartType = chartParameters.chartType;
        if (this.rawData && this.chart) {
            this.prepareChart();
        }
    }

    /**
     * clear data and update chart
     */
    refreshChart(): void {
        this.initQueries();
        this.clearCanvas();
        this.prepareChart();
    }

    initQueries(): void {
        this.rawData = [
            this.newSeries(this.queryText),
            ...this.comparedQueries.state$.value.compare.map(this.newSeries)
        ];
    }

    /** if a chart is active, clear canvas and reset chart object */
    clearCanvas(): void {
        if (this.chart) {
            // clear canvas an reset chart object
            this.chart.destroy();
            this.chart = undefined;
        }
    }

    /** update the queries in the graph to the input array. Preserve results if possible, and kick off loading the rest. */
    updateQueries(queries: string[]) {
        if (this.rawData) {
            this.rawData = queries.map((queryText) => {
                const existingSeries = this.rawData.find(
                    (series) => series.queryText === queryText
                );
                return existingSeries || this.newSeries(queryText);
            });
            this.prepareChart();
        }
    }

    /** make a blank series object */
    newSeries(queryText: string): BarchartSeries<DataPoint> {
        return {
            queryText,
            data: [],
            total_doc_count: 0,
            searchRatio: 1.0,
        };
    }

    /** Show a loading spinner and load data for the graph.
     * This function should be called after (potential) changes to parameters.
     */
    prepareChart() {
        showLoading(this.isLoading$, this.loadData());
    }

    /** load data for the graph (if needed), update the graph and freqtable. */
    loadData(): Promise<void> {
        // load data if needed
        return this.requestDocumentData()
            .then(
                this.frequencyMeasure === 'tokens'
                    ? this.requestTermFrequencyData.bind(this)
                    : _.identity
            )
            .then((rawData) => {
                this.rawData = rawData;

                if (!this.rawData.length) {
                    this.error.emit({ message: 'No results' });
                }

                // initialise or update chart
                this.setChart();

                // update freqtable
                this.setTableHeaders();
                this.setTableData();

                // load zoomed-in data if needed
                if (this.isZoomedIn) {
                    this.onZoomIn(this.chart, true);
                }
            });
    }

    /** Retrieve all document frequencies and store in `rawData`.
     * Document frequencies are only loaded if they are not already in the data. */
    requestDocumentData(): Promise<typeof this.rawData> {
        const dataPromises = this.rawData.map((series) => {
            if (!series.data.length) {
                // retrieve data if it was not already loaded
                return this.getSeriesDocumentData(series);
            } else {
                return series;
            }
        });

        return Promise.all(dataPromises).then(
            this.checkDocumentLimitExceeded.bind(this)
        );
    }

    selectSearchFields(queryModel: QueryModel) {
        if (this.frequencyMeasure === 'documents') {
            return queryModel;
        } else {
            const mainContentFields = this.corpus.fields.filter(
                (field) =>
                    field.searchable && field.displayType === 'text_content'
            );
            const queryModelCopy = queryModel.clone();
            queryModelCopy.setParams({searchFields: mainContentFields});
            return queryModelCopy;
        }
    }

    /**
     * Convert the result from an document search into a data series object.
     * - Converts to the relevant DataPoint type using `aggregateResultToDataPoint`
     * - Adds the total document count and search ratio for retrieving term frequencies.
     * - Adds the relative document count.
     *
     * @param result result from aggregation search
     * @param series series object that this data belongs to
     * @param setSearchRatio whether the search ratio should be reset. Defaults to `true`,
     * may be set to `false` when loading a portion of the series during zoom.
     * @returns a copy of the series with the document counts included.
     */
    docCountResultIntoSeries(
        result: AggregateResult[],
        series: BarchartSeries<DataPoint>,
        setSearchRatio = true
    ): BarchartSeries<DataPoint> {
        let data = result.map(this.aggregateResultToDataPoint);
        const total_doc_count = this.totalDocCount(result);
        const searchRatio = setSearchRatio
            ? this.documentLimit / total_doc_count
            : series.searchRatio;
        data = this.includeRelativeDocCount(data, total_doc_count);
        return {
            data,
            total_doc_count,
            searchRatio,
            queryText: series.queryText,
        };
    }

    /** convert the output of an aggregation search to the relevant result type */
    abstract aggregateResultToDataPoint(cat: AggregateResult): DataPoint;

    /** fill in the `relative_doc_count` property for an array of datapoints.
     */
    includeRelativeDocCount(data: DataPoint[], total: number): DataPoint[] {
        return data.map((item) => {
            const result = _.clone(item);
            result.relative_doc_count = result.doc_count / total;
            return result;
        });
    }

    /**
     * Check whether any series found more documents than the document limit.
     * This means that not all documents will be read when counting term frequency.
     */
    checkDocumentLimitExceeded(
        rawData: typeof this.rawData
    ): typeof this.rawData {
        this.documentLimitExceeded =
            rawData.find((series) => series.searchRatio < 1) !== undefined;
        return rawData;
    }

    /** Retrieve all term frequencies and store in `rawData`.
     * Term frequencies are only loaded if they were not already there.
     */
    requestTermFrequencyData(rawData: typeof this.rawData): Promise<BarchartSeries<DataPoint>[]> {
        // cancel and stop polling running tasks
        this.stopPolling$.next();
        const dataPromises = rawData.map(series => {
            if (series.queryText && series.data.length && series.data[0].match_count === undefined) {
                // retrieve data if it was not already loaded
                return this.getTermFrequencies(series, this.queryModel);
            } else {
                return series;
            }
        });

        return Promise.all(dataPromises).then(
            this.checkTotalTokenCount.bind(this)
        );
    }

    checkTotalTokenCount(rawData: typeof this.rawData): typeof this.rawData {
        const totalTokenCountAvailable =
            rawData.find((series) =>
                series.data.find((cat) => cat.token_count)
            ) !== undefined;
        if (
            this.frequencyMeasure === 'tokens' &&
            totalTokenCountAvailable &&
            !this.totalTokenCountAvailable
        ) {
            this.normalizer = 'terms';
        }
        this.totalTokenCountAvailable = totalTokenCountAvailable;
        return rawData;
    }

    getTermFrequencies(
        series: BarchartSeries<DataPoint>,
        queryModel: QueryModel
    ): Promise<BarchartSeries<DataPoint>> {
        this.dataHasLoaded = false;
        const queryModelCopy = this.queryModelForSeries(series, queryModel);
        return new Promise((resolve, reject) => {
            this.requestSeriesTermFrequency(series, queryModelCopy).then(response => {
                this.tasksToCancel = response.task_ids;
                const poller$ = this.apiService.pollTasks(this.tasksToCancel, this.stopPolling$);
                poller$.subscribe({
                    error: (error) => {
                        this.onFailure(error);
                        reject(error);
                    },
                    next: (result) => {
                        resolve(this.processSeriesTermFrequency(result['results'], series));
                    },
                    complete: () => {
                        // abort tasks if the Observable is completed via takeUntil
                        if (!this.dataHasLoaded) {
                            this.apiService.abortTasks({ task_ids: this.tasksToCancel });
                        }
                    }
                });
            });
        });
    }

    onFailure(error) {
        console.error(error);
        this.error.emit(`could not load results: ${error.message}`);
    }

    abstract requestSeriesTermFrequency(series: BarchartSeries<DataPoint>, queryModel: QueryModel): Promise<TaskResult>;

    abstract makeTermFrequencyBins(series: BarchartSeries<DataPoint>);

    processSeriesTermFrequency(results: TermFrequencyResult[], series: BarchartSeries<DataPoint>): BarchartSeries<DataPoint> {
        this.dataHasLoaded = true;
        series.data = _.zip(series.data, results).map(pair => {
            const [bin, res] = pair;
            return this.addTermFrequencyToCategory(res, bin);
        });
        return series;
    };


    /** total document count for a data array */
    totalDocCount(data: AggregateResult[]) {
        return _.sumBy(data, (item) => item.doc_count);
    }

    /**
     * calculate the maximum number of documents to read through in a bin
     * when determining term frequency.
     */
    documentLimitForCategory(
        cat: DataPoint,
        series: BarchartSeries<DataPoint>
    ): number {
        return _.min([
            this.documentLimit,
            _.ceil(cat.doc_count * series.searchRatio),
        ]);
    }

    /**
     * add term frequency data to a DataPoint object
     *
     * @param result output from request for term frequencies
     * @param cat DataPoint object where the data should be added
     */
    addTermFrequencyToCategory(
        data: TermFrequencyResult,
        cat: DataPoint
    ): DataPoint {
        cat.match_count = data.match_count;
        cat.total_doc_count = data.total_doc_count;
        cat.token_count = data.token_count;
        cat.matches_by_doc_count = data.match_count / data.total_doc_count;
        cat.matches_by_token_count = data.token_count
            ? data.match_count / data.token_count
            : undefined;
        return cat;
    }

    /** Request and fill in doc counts for a series */
    getSeriesDocumentData(
        series: BarchartSeries<DataPoint>,
        queryModel: QueryModel = this.queryModel,
        setSearchRatio = true
    ): Promise<BarchartSeries<DataPoint>> {
        const queryModelCopy = this.queryModelForSeries(series, queryModel);

        return this.requestSeriesDocCounts(queryModelCopy).then((result) =>
            this.docCountResultIntoSeries(result, series, setSearchRatio)
        );
    }

    /** adapt query model to fit series: use correct search fields and query text */
    queryModelForSeries(
        series: BarchartSeries<DataPoint>,
        queryModel: QueryModel
    ) {
        return this.selectSearchFields(
            this.setQueryText(queryModel, series.queryText)
        );
    }

    /** Request doc counts for a series */
    abstract requestSeriesDocCounts(
        queryModel: QueryModel
    ): Promise<AggregateResult[]>;

    requestFullData() {
        this.fullDataRequest()
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

    abstract fullDataRequest(): Promise<TaskResult>;

    /** update or initialise chart (should be ran after updates to `rawData`) */
    setChart(): void {
        if (this.chart) {
            this.updateChartData();
        } else {
            this.initChart();
        }
    }
    /** select the columns/headers for the frequency table */
    abstract setTableHeaders(): void;
    /** code to be executed when zooming in, or when parameters are updated while zoomed in */
    onZoomIn(chart, triggeredByDataUpdate = false) {}
    /** options for the chart.
     *
     * @param datasets array of dataset objects for the chart
     */
    abstract chartOptions(datasets);

    /** initalise a new chart */
    initChart() {
        const labels = this.getLabels();
        const datasets = this.getDatasets();
        const options = this.chartOptions(datasets);

        this.chart = new Chart(barchartID, {
            type: 'bar',
            data: {
                labels,
                datasets,
            },
            plugins: [Zoom],
            options,
        });

        this.chart.canvas.ondblclick = (event) => this.zoomOut();
    }

    /** reset zooming */
    zoomOut(): void {
        this.chart.resetZoom();
    }

    /** After updating `rawData`, this executes the update in the chart. */
    updateChartData() {
        const labels = this.getLabels();
        const datasets = this.getDatasets();
        this.chart.options = this.chartOptions(datasets);
        this.chart.data.labels = labels;
        this.chart.data.datasets = datasets;
        this.chart.options.plugins.legend.display = datasets.length > 1;
        this.chart.update();
    }

    /** Return x-axis labels for the chartJS dataset.
     * Can be left undefined depending on data format.
     */
    getLabels(): string[] {
        return undefined;
    }

    /** return chartJS dataset objects based on rawData */
    abstract getDatasets(): any[];

    /**
     * Show the zooming hint once per session, hide automatically with a delay
     * when the user moves the mouse.
     */
    setupZoomHint() {
        if (!sessionStorage.getItem(hintSeenSessionStorageKey)) {
            sessionStorage.setItem(hintSeenSessionStorageKey, 'true');
            this.showHint = true;
            const hider = _.debounce(() => {
                this.showHint = false;
                document.body.removeEventListener('mousemove', hider);
            }, hintHidingDebounceTime);
            _.delay(() => {
                document.body.addEventListener('mousemove', hider);
            }, hintHidingMinDelay);
        }
    }

    formatValue(normalizer: string): (value?: number) => string | undefined {
        if (normalizer === 'percent') {
            return (value?: number) => {
                if (value !== undefined && value !== null) {
                    return `${_.round(100 * value, 1)}%`;
                }
            };
        } else if (normalizer === 'documents' || normalizer === 'terms') {
            return (value: number) => {
                if (value !== undefined && value !== null) {
                    return value.toPrecision(2);
                }
            };
        } else {
            return (value: number) => {
                if (value !== undefined && value !== null) {
                    return value.toString();
                }
            };
        }
    }

    get formatDownloadValue(): (value: number) => string {
        if (this.normalizer === 'percent') {
            return (value: number) => {
                if (value !== undefined && value !== null) {
                    return `${_.round(100 * value, 1)}`;
                }
            };
        } else {
            return (value: number) => value.toString();
        }
    }

    /** return a copy of a query model with the query text set to the given value */
    setQueryText(query: QueryModel, queryText: string): QueryModel {
        const queryModelCopy = query.clone();
        queryModelCopy.setQueryText(queryText);
        return queryModelCopy;
    }

    /** assemble the array of table data */
    setTableData() {
        if (this.rawData && this.rawData.length) {
            this.tableData = _.flatMap(this.rawData, (series) =>
                series.data.map((item) => {
                    const result = _.cloneDeep(item) as any;
                    result.queryText = series.queryText;
                    return result;
                })
            );
        }
    }

    /** which key of a DataPoint object should be used as the y-axis value */
    get currentValueKey(): string {
        return this.valueKeys[this.frequencyMeasure][this.normalizer];
    }

    /**
     * Percentage of documents that was actually read when determining term frequency.
     * This differs per series, but user message only gives one value, currently the minimum.
     */
    get percentageDocumentsSearched() {
        if (this.rawData) {
            return _.round(
                100 * _.min(this.rawData.map((series) => series.searchRatio)),
                1
            );
        }
    }

    /**
     * Whether the graph is zoomed in on the x-axis.
     */
    get isZoomedIn(): boolean {
        // If no zooming-related scripts are implemented, just return false
        return false;
    }

    get searchFields(): string {
        if (this.corpus && this.queryModel) {
            const searchFields = this.selectSearchFields(
                this.queryModel
            ).searchFields;

            const displayNames = searchFields.map((field) => field.displayName);

            return displayNames.join(', ');
        }

        return 'all fields';
    }

    chartTitle() {
        const queryTexts = this.rawData.map((series) => series.queryText);
        if (this.queryText == null && this.rawData.length === 1) {
            return `Frequency of documents by ${this.visualizedField.displayName} (n of ${this.frequencyMeasure}, ${this.normalizer})`;
        } else {
            const normalizationText = ['raw', 'percent'].includes(
                this.normalizer
            )
                ? ''
                : `, normalized by ${this.normalizer}`;
            return `Frequency of '${queryTexts.join(', ')}' by ${
                this.visualizedField.displayName
            } (n of ${this.frequencyMeasure}${normalizationText})`;
        }
    }

    get queryText(): string {
        if (this.queryModel) {
            return this.queryModel.queryText;
        }
    }
}
