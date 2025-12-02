import { Component, OnChanges, OnInit } from '@angular/core';
import * as _ from 'lodash';

import {
    HistogramDataPoint,
    HistogramSeries,
    MultipleChoiceFilterOptions,
    QueryModel,
    RangeFilterOptions,
} from '@models/index';
import { selectColor } from '@utils/select-color';
import { BarchartDirective } from './barchart.directive';
import { TermsAggregator, TermsResult } from '@models/aggregation';

function formatXAxisLabel(value): string {
    const label = this.getLabelForValue(value); // from chartJS api
    const max_length = 30;
    if (label.length > max_length) {
        return `${label.slice(0, max_length)}...`;
    }
    return label;
}

@Component({
    selector: 'ia-histogram',
    templateUrl: './histogram.component.html',
    styleUrls: ['./histogram.component.scss'],
    standalone: false
})
export class HistogramComponent
    extends BarchartDirective<TermsResult, HistogramDataPoint>
    implements OnInit, OnChanges {
    /** On what property should the data be sorted? */
    get defaultSort(): string {
        if (this.visualizedField && this.visualizedField.visualizationSort) {
            return 'key';
        }
        return this.currentValueKey;
    }

    /** specify aggregator object based on visualised field;
     * used in document requests.
     */
    getAggregator(): TermsAggregator {
        let size = 100;

        const filterOptions = this.visualizedField.filterOptions;
        if (filterOptions?.name === 'MultipleChoiceFilter') {
            size = (filterOptions as MultipleChoiceFilterOptions).option_count;
        } else if (filterOptions?.name === 'RangeFilter') {
            const filterRange =
                (filterOptions as RangeFilterOptions).upper -
                (filterOptions as RangeFilterOptions).lower;
            size = _.max([size, filterRange])
        }
        return new TermsAggregator(this.visualizedField, size);
    }

    requestSeriesDocCounts(queryModel: QueryModel) {
        const aggregator = this.getAggregator();

        return this.searchService.aggregateSearch(this.corpus, queryModel, aggregator);
    }

    aggregateResultToDataPoint(cat: TermsResult) {
        return cat;
    }

    requestSeriesTermFrequency(
        series: HistogramSeries,
        queryModel: QueryModel
    ) {
        const bins = this.makeTermFrequencyBins(series);
        return this.visualizationService.aggregateTermFrequencySearch(
            this.corpus,
            queryModel,
            this.visualizedField.name,
            bins
        );
    }

    makeTermFrequencyBins(series: HistogramSeries) {
        return series.data.map((bin) => ({
            fieldValue: bin.key,
            size: this.documentLimitForCategory(bin, series),
        }));
    }

    fullDataRequest() {
        const paramsPerSeries = this.rawData.map((series) => {
            const queryModel = this.queryModelForSeries(
                series,
                this.queryModel
            );
            const bins = this.makeTermFrequencyBins(series);
            return this.visualizationService.makeAggregateTermFrequencyParameters(
                this.corpus,
                queryModel,
                this.visualizedField.name,
                bins
            );
        });
        return this.apiService.requestFullData({
            visualization: 'aggregate_term_frequency',
            parameters: paramsPerSeries,
            corpus_name: this.corpus.name,
        });
    }

    getLabels(): string[] {
        // make an array of all unique labels and sort

        if (this.rawData) {
            const all_labels = _.flatMap(this.rawData, (series) =>
                series.data.map((item) => item.key)
            );
            const labels = all_labels.filter(
                (key, index) => all_labels.indexOf(key) === index
            );
            let sorted_labels: string[];
            if (this.visualizedField.visualizationSort === 'key') {
                sorted_labels = labels.sort();
            } else {
                const valueKey = this.currentValueKey;
                sorted_labels = _.sortBy(labels, (label) =>
                    _.sumBy(this.rawData, (series) => {
                        const item = series.data.find((i) => i.key === label);
                        return -1 * (item ? item[valueKey] : 0);
                    })
                );
            }
            return sorted_labels;
        }
    }

    getDatasets() {
        const labels = this.getLabels();
        const valueKey = this.currentValueKey;

        return this.rawData.map((series, seriesIndex) => ({
            type: this.chartType,
            label: series.queryText ? series.queryText : '(no query)',
            data: labels.map((key) => {
                const item = series.data.find((i) => i.key === key);
                return item ? item[valueKey] : 0;
            }),
            backgroundColor: selectColor(this.palette, seriesIndex),
            hoverBackgroundColor: selectColor(this.palette, seriesIndex),
            pointRadius: 2.5,
            pointHoverRadius: 5,
        }));
    }

    chartOptions(datasets: any[]) {
        const xLabel = this.visualizedField.displayName
            ? this.visualizedField.displayName
            : this.visualizedField.name;
        const options = this.basicChartOptions;
        options.plugins.title.text = this.chartTitle();
        options.scales.x.type = 'category';
        (options.scales.x as any).title.text = xLabel;
        options.scales.x.ticks = { callback: formatXAxisLabel };
        options.plugins.tooltip = {
            callbacks: {
                label: (tooltipItem) => {
                    const value = tooltipItem.raw as number;
                    return this.formatValue(this.normalizer)(value);
                },
            },
        };
        options.plugins.legend = { display: datasets.length > 1 };
        return options;
    }

    setTableHeaders() {
        /*
        Provides the table headers to the freqTable component. Determines optional headers.
        */
        const label = this.visualizedField.displayName
            ? this.visualizedField.displayName
            : this.visualizedField.name;
        const rightColumnName =
            this.normalizer === 'raw' ? 'Frequency' : 'Relative frequency';
        const valueKey = this.currentValueKey;

        if (this.rawData.length > 1) {
            // if there are several queries, fulltable is disabled
            this.tableHeaders = [
                { key: 'key', label, isSecondaryFactor: true },
                { key: 'queryText', label: 'Query', isMainFactor: true },
                {
                    key: valueKey,
                    label: rightColumnName,
                    format: this.formatValue(this.normalizer),
                    formatDownload: this.formatDownloadValue,
                },
            ];
        } else {
            this.tableHeaders = [
                { key: 'key', label },
                {
                    key: 'doc_count',
                    label: 'Document Frequency',
                    format: this.formatValue('raw'),
                    formatDownload: this.formatDownloadValue,
                    isOptional: 'doc_count' !== valueKey,
                },
                {
                    key: 'relative_doc_count',
                    label: 'Document Frequency (%)',
                    format: this.formatValue('percent'),
                    formatDownload: this.formatDownloadValue,
                    isOptional: 'relative_doc_count' !== valueKey,
                },
            ];
            if (this.frequencyMeasure == 'tokens') {
                // Headers related to tokens should not be applied to document visualizations
                this.tableHeaders = this.tableHeaders.concat([
                    {
                        key: 'match_count',
                        label: 'Token Frequency',
                        format: this.formatValue('raw'),
                        formatDownload: this.formatDownloadValue,
                        isOptional: 'match_count' !== valueKey,
                    },
                    {
                        key: 'matches_by_doc_count',
                        label: 'Relative Frequency (documents)',
                        format: this.formatValue('documents'),
                        formatDownload: this.formatDownloadValue,
                        isOptional: 'matches_by_doc_count' !== valueKey,
                    },
                    {
                        key: 'matches_by_token_count',
                        label: 'Relative Frequency (terms)',
                        format: this.formatValue('terms'),
                        formatDownload: this.formatDownloadValue,
                        isOptional: 'matches_by_token_count' !== valueKey,
                    },
                ]);
            }
        }
    }
}
