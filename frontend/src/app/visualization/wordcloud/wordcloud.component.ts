import {
    Component, ElementRef, input, Input, OnChanges, OnDestroy, output, SimpleChanges,
    ViewChild
} from '@angular/core';
import {
    MostFrequentWordsResult, QueryModel, FreqTableHeaders,
} from '@models/index';
import { VisualizationService } from '@services/visualization.service';
import * as _ from 'lodash';
import { FrequentWordsResults } from '@models/frequent-words';
import { RouterStoreService } from '@app/store/router-store.service';
import embed, { VisualizationSpec } from 'vega-embed';
import { filter } from 'rxjs';

// maximum font size in px
const MIN_FONT_SIZE = 10;
const MAX_FONT_SIZE = 48;


const spec = (
    data: MostFrequentWordsResult[], palette: string[], width: number, height: number,
): VisualizationSpec => {
    const values = data.slice(0, 100);
    return {
        '$schema': 'https://vega.github.io/schema/vega/v6.json',
        width,
        height,
        padding: 0,
        signals: [
            {
                name: 'theme',
                description: 'Current site theme (light/dark)',
                bind: { element: '#current-theme' }
            }
        ],
        data: [
            {
                name: 'word_counts',
                values,
                transform: [
                    {
                        type: 'formula',
                        as: 'label',
                        expr: 'datum.key + ": " + toString(datum.doc_count)'
                    }
                ]
            }
        ],
        scales: [
            {
                name: 'color',
                type: 'ordinal',
                domain: { 'data': 'word_counts', field: 'key' },
                range: palette,
            }
        ],
        marks: [
            {
                type: 'text',
                from: { data: 'word_counts' },
                encode: {
                    enter: {
                        text: { field: 'key' },
                        align: { value: 'center' },
                        baseline: { value: 'alphabetic' },
                        tooltip: { field: 'label' },
                    },
                    update: {
                        fill: { scale: 'color', field: 'key' },
                    },
                    hover: {
                        fill:  {signal: 'theme === "dark" ? "white" : "black"'}
                    }
                },
                transform: [
                    {
                        type: 'wordcloud',
                        size: [width, height],
                        text: { field: 'key' },
                        fontSize: { field: 'datum.doc_count' },
                        fontSizeRange: [MIN_FONT_SIZE, MAX_FONT_SIZE],
                        padding: 2
                    }
                ]
            }
        ]
    }
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
    @ViewChild('chart') chart!: ElementRef<HTMLElement>;

    palette = input.required<string[]>();
    wordcloudError = output<string>();

    results: FrequentWordsResults;
    chartData: MostFrequentWordsResult[] = [];

    tableHeaders: FreqTableHeaders = [
        { key: 'key', label: 'Term' },
        { key: 'doc_count', label: 'Frequency' },
    ];

    constructor(
        private routerStoreService: RouterStoreService,
        private visualizationService: VisualizationService
    ) { }

    ngOnChanges(changes: SimpleChanges) {
        if (changes.queryModel) {
            this.results?.complete();

            this.results = new FrequentWordsResults(
                this.routerStoreService, this.queryModel, this.visualizationService
            );

            // result$ and error$ are completed when this.results.complete() is called
            // so these subscriptions are closed at that point
            this.results.result$.subscribe(data => this.makeChart(data));
            this.results.error$.pipe(
                filter(_.identity),
            ).subscribe(error => this.emitError(error));
        } else if (changes.palette) {
            this.renderChart();
        }
    }

    ngOnDestroy(): void {
        this.results?.complete();
    }

    emitError(error?: { message: string }) {
        console.error(error);
        this.wordcloudError.emit(error?.message ?? 'Unknown error');
    }

    makeChart(data: MostFrequentWordsResult[]) {
        this.chartData = data;
        this.renderChart();
    }

    private renderChart(): void {
        const width = this.chart.nativeElement.offsetWidth;
        const aspectRatio = 2 / 3;
        const height = width * aspectRatio;
        const data: VisualizationSpec = spec(
            this.chartData, this.palette(), width, height
        );

        embed(this.chart.nativeElement, data, {
            mode: 'vega',
            renderer: 'canvas',
            width: width,
            height: height,
            actions: false,
            tooltip: true,
        }).catch(error => {
            console.error(error);
        });
    }
}
