import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import * as _ from 'lodash';
import { ParamDirective } from '@app/param/param-directive';
import { Normalizer, ChartType, ChartParameters } from '@models';
import { ParamService } from '@services';

@Component({
    selector: 'ia-barchart-options',
    templateUrl: './barchart-options.component.html',
    styleUrls: ['./barchart-options.component.scss'],
    standalone: false
})
export class BarchartOptionsComponent
    extends ParamDirective
    implements OnChanges {
    @Input() queryText: string;
    @Input() showTokenCountOption: boolean;
    @Input() isLoading: boolean;

    @Input() freqTable: boolean;
    @Input() frequencyMeasure: 'documents' | 'tokens' = 'documents';
    @Input() histogram: boolean;

    @Output() chartParameters = new EventEmitter<ChartParameters>();
    @Output() queriesChanged = new EventEmitter<string[]>();

    currentNormalizer: Normalizer;

    currentChartType: ChartType = 'bar';

    showEdit = false;

    nullableParameters = ['normalize'];

    constructor(
        route: ActivatedRoute,
        router: Router,
        paramService: ParamService,
    ) {
        super(route, router, paramService);
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (
            changes.showTokenCountOption &&
            changes.showTokenCountOption.currentValue &&
            this.frequencyMeasure === 'tokens'
        ) {
            this.currentNormalizer = 'terms';
        }
    }

    onChartParametersChange(): void {
        const chartParameters: ChartParameters = {
            normalizer: this.currentNormalizer,
            chartType: this.currentChartType,
        };
        this.chartParameters.emit(chartParameters);
        const route = {};
        if (this.currentNormalizer !== 'raw' || 'terms') {
            route['normalize'] = this.currentNormalizer;
        } else {
            route['normalize'] = null;
        }

        this.setParams(route);
    }

    initialize() {}

    teardown() {}

    setStateFromParams(params: ParamMap) {
        // show term comparison editor if there are terms in the route ;
        // don't hide the editor if already displayed
        this.showEdit = this.showEdit || params.has('compareTerms');
        if (params.has('normalize')) {
            this.currentNormalizer = params.get('normalize') as Normalizer;
        } else {
            if (
                this.frequencyMeasure === 'documents' ||
                !this.showTokenCountOption
            ) {
                this.currentNormalizer = 'raw';
            } else {
                this.currentNormalizer = 'terms';
            }
        }
    }

    updateQueries(queries: string[]) {
        if (_.isEqual(queries, [this.queryText])) {
            this.showEdit = false;
        }
        this.queriesChanged.emit(queries);
    }

}
