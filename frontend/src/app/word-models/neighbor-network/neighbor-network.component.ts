import { AfterViewInit, Component, ElementRef, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { Corpus, FreqTableHeaders } from '@models';
import { WordmodelsService } from '@services';
import { Theme, ThemeService } from '@services/theme.service';
import { BehaviorSubject } from 'rxjs';
import embed from 'vega-embed';

@Component({
    selector: 'ia-neighbor-network',
    templateUrl: './neighbor-network.component.html',
    styleUrl: './neighbor-network.component.scss',
    standalone: false,
})
export class NeighborNetworkComponent implements OnChanges, AfterViewInit {
    @Input({required: true}) corpus!: Corpus;
    @Input({required: true}) queryText!: string;
    @Input() asTable: boolean;

    @ViewChild('chart') chart!: ElementRef;
    @ViewChild('theme') themeInput!: ElementRef;

    data: any;

    tableHeaders: FreqTableHeaders = [
        {
            key: 'term1',
            label: 'Term 1',
        },
        {
            key: 'term2',
            label: 'Term 2',
        },
        {
            key: 'timeframe',
            label: 'Timeframe',
        },
        {
            key: 'similarity',
            label: 'Similarity'
        }
    ];

    constructor(
        private wordModelsService: WordmodelsService,
        private themeService: ThemeService,
    ) { }

    ngAfterViewInit() {
        this.themeService.theme$.subscribe(
            theme => this.updateTheme(theme)
        );
    }

    ngOnChanges(changes: SimpleChanges): void {
        this.getData()
    }

    getData() {
        this.wordModelsService.getNeighborNetwork(
            this.queryText, this.corpus.name, 5
        ).subscribe(this.onDataLoaded.bind(this));
    }

    onDataLoaded(res) {
        this.data = res;
        this.renderChart(res['graph']);
    }

    renderChart(data): void {
        const aspectRatio = 2 / 3;
        const width = this.chart.nativeElement.offsetWidth;
        const height = width * aspectRatio;

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

    updateTheme(theme: Theme) {
        const el = this.themeInput.nativeElement as HTMLInputElement;
        el.value = theme;
        el.dispatchEvent(new Event('input'));
    }
}
