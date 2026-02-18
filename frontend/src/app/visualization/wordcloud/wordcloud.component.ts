import {
    Component, EventEmitter, Input, OnChanges, OnDestroy, Output, SimpleChanges
} from '@angular/core';


import {
    MostFrequentWordsResult,
    QueryModel,
    FreqTableHeaders,
} from '@models/index';
import { VisualizationService } from '@services/visualization.service';
import {
    Chart,
    ChartData,
    ChartDataset,
    ChartOptions,
    ScriptableContext,
    TooltipItem,
} from 'chart.js';
import { WordCloudChart } from 'chartjs-chart-wordcloud';
import * as _ from 'lodash';
import { selectColor } from '@utils/select-color';
import { FrequentWordsResults } from '@models/frequent-words';
import { RouterStoreService } from '@app/store/router-store.service';

// maximum font size in px
const MIN_FONT_SIZE = 10;
const MAX_FONT_SIZE = 48;

/** returns a scaling function for words based on their frequency */
export const sizeScale = (min: number, max: number): (frequency: number) => number => {
    const normalize = unitScale(min, max);
    const sizeRange = MAX_FONT_SIZE - MIN_FONT_SIZE;
    return (frequency: number) =>
        MIN_FONT_SIZE + sizeRange * normalize(frequency);
};

/** returns a function that maps values in [min, max] onto [0,1]
 */
const unitScale = (min: number, max: number): (frequency: number) => number => {
    const frequencyRange = (max - min) || 1; // avoid zero-division if all values are the same
    return (frequency: number) => (frequency - min) / frequencyRange;
};

@Component({
    selector: 'ia-wordcloud',
    templateUrl: './wordcloud.component.html',
    styleUrls: ['./wordcloud.component.scss'],
    standalone: false
})
export class WordcloudComponent implements OnChanges, OnDestroy {
    @Input() queryModel: QueryModel;
    @Input() asTable: boolean;
    @Input() palette: string[];

    @Output() wordcloudError = new EventEmitter();

    results: FrequentWordsResults;

    tableHeaders: FreqTableHeaders = [
        { key: 'key', label: 'Term' },
        { key: 'doc_count', label: 'Frequency' },
    ];

    private chart: Chart;

    constructor(
        private routerStoreService: RouterStoreService,
        private visualizationService: VisualizationService
    ) {}

    ngOnChanges(changes: SimpleChanges) {
        if (changes.queryModel) {
            this.results?.complete();

            this.results = new FrequentWordsResults(
                this.routerStoreService, this.queryModel, this.visualizationService
            );

            // result$ and error$ are completed when this.results.complete() is called
            // so these subscriptions are closed at that point
            this.results.result$.subscribe(data => this.makeChart(data));
            this.results.error$.subscribe(error => this.emitError(error));
        } else if (changes.palette) {
            this.updatePalette();
        }
    }

    ngOnDestroy(): void {
        this.results?.complete();
        this.chart?.destroy();
    }

    emitError(error?: { message: string }) {
        this.wordcloudError.emit(error?.message);
    }

    makeChart(result: MostFrequentWordsResult[]) {
        if (!this.asTable) {
            const data: ChartData<'wordCloud'> = this.chartData(
                result,
            ) as ChartData<'wordCloud'>;
            const options = this.chartOptions(result);

            if (this.chart) {
                this.chart.data = data;
                this.chart.update();
            } else {
                this.chart = new WordCloudChart('wordcloud', { data, options });
            }
        }
    }

    private chartData(result: MostFrequentWordsResult[]): ChartData<'wordCloud'> {
        if (result) {
            const labels = this.chartLabels(result);
            const datasets = [this.chartDataset(result)];
            return { labels, datasets };
        }
        return { labels: [], datasets: [] };
    }

    private chartLabels(result: MostFrequentWordsResult[]): string[] {
        return result.map((item) => item.key);
    }

    private chartDataset(result: MostFrequentWordsResult[]): ChartDataset<'wordCloud'> {
        const frequencies = result.map((item) => item.doc_count);
        const scale = sizeScale(_.min(frequencies), _.max(frequencies));
        const sizes = frequencies.map(scale);

        return {
            label: 'Frequency',
            data: sizes,
            color: this.datasetColor(this.palette),
        };
    }

    private updatePalette() {
        const dataset = _.first(this.chart?.data?.datasets) as ChartDataset<'wordCloud'>;
        if (dataset) {
            dataset.color = this.datasetColor(this.palette);
            this.chart.update();
        }
    }

    private datasetColor(palette: string[]): (context: ScriptableContext<'wordCloud'>) => string {
        return (context) => selectColor(palette, context.dataIndex);
    }

    private chartOptions(data: MostFrequentWordsResult[]): ChartOptions<'wordCloud'> {
        return {
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    displayColors: false,
                    callbacks: {
                        label: (item: TooltipItem<'wordCloud'>) =>
                            data[
                                item.dataIndex
                            ].doc_count.toString(),
                    },
                },
            },
        };
    }
}
