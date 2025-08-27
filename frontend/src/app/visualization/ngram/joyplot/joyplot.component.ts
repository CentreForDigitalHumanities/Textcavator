import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Chart, ChartData, ChartOptions } from 'chart.js';
import * as _ from 'lodash';
import { NgramResults } from '@models';
import { selectColor } from '@utils/select-color';
import { setThemefaults } from 'app/visualization/chartjs-utils';

@Component({
    selector: 'ia-joyplot',
    templateUrl: './joyplot.component.html',
    styleUrls: ['./joyplot.component.scss'],
    standalone: false
})
export class JoyplotComponent implements OnChanges {
    @Input() data: NgramResults;
    @Input() formatValue: (x: number) => string;
    @Input() palette: string[];
    @Input() quantity = 'frequency';
    @Input() comparedByQuantity = 'date';

    maxDataPoint: number;

    fixLineGraphHeights = false;

    terms: string[];
    timeLabels: string[] = [];

    chartData: any;
    chartOptions: ChartOptions;
    chart: Chart;

    constructor() {
        setThemefaults(Chart.defaults);
    }

    get multipleTimeIntervals(): boolean {
        return this.timeLabels && this.timeLabels.length > 1;
    }


    ngOnChanges(changes: SimpleChanges): void {
        if (this.data) {
            const updateAspectRatio = changes.data && changes.data.currentValue?.words.length !== changes.data.previousValue?.words.length;
            this.update(this.data, updateAspectRatio);
        }
    }

    update(data, updateAspectRatio = true) {
        this.setmaxDataPoint(data);
        this.chartData = this.makeChartdata(data);
        this.chartOptions = this.makeChartOptions(this.chartData);

        if (this.chart) {
            if (updateAspectRatio) {
                this.resetChartHeight();
            }
            this.chart.data = this.chartData;
            this.chart.options = this.chartOptions;
            this.chart.update();
        } else {
            this.chart = this.makeChart();
        }
    }


    makeChartdata(result: NgramResults): any {
        this.timeLabels = result.time_points;
        this.terms = result.words.map(item => item.label);

        const datasets = this.multipleTimeIntervals ? this.timeDataSets(result) : [];

        const totals = result.words.map(item => _.sum(item.data));
        const totalsData = totals.map((value, index) => ({
            x: value,
            y: index,
            ngram: this.terms[index],
        }));
        const colors = totals.map((value, index) => selectColor(this.palette, index));

        const totalsDataset = {
            type: 'bar',
            xAxisID: 'xTotal',
            indexAxis: 'y',
            label: `total ${this.quantity}`,
            backgroundColor: colors,
            hoverBackgroundColor: colors,
            data: totalsData,
        };

        datasets.push(totalsDataset);

        return {
            labels: this.timeLabels,
            datasets,
        };
    }

    timeDataSets(result: NgramResults): any[] {
        return _.reverse( // reverse drawing order so datasets are drawn OVER the one above them
        result.words.map((item, index) => {
            const points = this.getDataPoints(item.data, index);
            return {
                type: 'line',
                xAxisID: 'x',
                label: item.label,
                data: points,
                borderColor: selectColor(this.palette, index),
                fill: {
                    target: {value: index},
                    above: this.getFillColor.bind(this),
                },
            };
        })
    );


    }

    getDataPoints(data: number[], ngramIndex: number) {
        const yValues = this.getYValues(data, ngramIndex);

        return _.zip(data, yValues).map(([value, y], x) => ({
            y,
            value,
            x,
        }));
    }

    getYValues(data: number[], ngramIndex: number): number[] {
        const scaled = this.scaleValues(data);
        return scaled.map(value => ngramIndex - value);
    }

    scaleValues(data: number[]): number[] {
        const max = this.fixLineGraphHeights ? _.max(data) : this.maxDataPoint;
        return data.map(point => 1.1 * point / max);
    }

    getFillColor(context) {
        const borderColor = context.dataset.borderColor as string;

        if (borderColor.startsWith('#') && borderColor.length === 7) { // hex color
            const red = parseInt(borderColor.slice(1, 3), 16);
            const green = parseInt(borderColor.slice(3, 5), 16);
            const blue = parseInt(borderColor.slice(5, 7), 16);

            return `rgba(${red}, ${green}, ${blue}, 0.5)`;
        }
    }

    makeChartOptions(data: ChartData): ChartOptions {
        const totalsData = _.last(data.datasets).data;
        const totals = totalsData.map((item: any) => item.x);
        const maxTotal = _.max(totals);

        const numberOfRows = this.terms.length;
        const xLabel = `${this.quantity} by ${this.comparedByQuantity}`;

        return {
            aspectRatio: 24 / (4 + numberOfRows),
            elements: {
                point: {
                    radius: 0,
                    hoverRadius: 0,
                }
            },
            scales: {
                xTotal: {
                    type: 'linear',
                    title: {
                        text: `total ${this.quantity}`,
                        display: true,
                    },
                    ticks: {
                        display: false,
                    },
                    max: maxTotal * 1.05,
                    position: 'top',
                    stack: '1',
                    stackWeight: 1.5,
                    display: true,
                },
                x: {
                    type: 'category',
                    display: this.timeLabels.length > 1,
                    title: {
                        text: xLabel,
                        display: true,
                    },
                    position: 'top',
                    stack: '1',
                    stackWeight: this.multipleTimeIntervals ? 8.5 : 0.01, // chartJS does not like stackWeight 0
                },
                y: {
                    reverse: true,
                    title: {
                        text: 'Ngram'
                    },
                    ticks: {
                        stepSize: 1,
                        callback: (val, index) => this.terms[val]
                    }
                },
            },
            plugins: {
                legend: { display: false },
                filler: {
                    propagate: true,
                },
                tooltip: {
                    callbacks: {
                        title: (tooltipItems) => {
                            const tooltipItem = tooltipItems[0];
                            if (tooltipItem.dataset.xAxisID === 'xTotal') {
                                return `total ${this.quantity}`;
                            } else {
                                return tooltipItem.label;
                            }
                        },
                        label: (tooltipItem) => {
                            let ngram: string;
                            let value: number;
                            if (tooltipItem.dataset.xAxisID === 'xTotal') {
                                ngram = (tooltipItem.raw as any).ngram;
                                value = (tooltipItem.raw as any).x;
                            } else {
                                ngram = tooltipItem.dataset.label;
                                value = (tooltipItem.raw as any).value;
                            }
                            return `${ngram}: ${this.formatValue(value)}`;
                        }
                    }
                }
            }
        };
    }


    makeChart() {
        return new Chart('chart', {
            type: 'line',
            data: this.chartData,
            options: this.chartOptions,
        });
    }


    resetChartHeight() {
        // updating aspect ratio has no effect if canvas height is set
        // set to null before updating
        this.chart.canvas.style.height = null;
        this.chart.canvas.height = null;
    }

    setmaxDataPoint(data: NgramResults) {
        this.maxDataPoint = _.max(
            _.map(data.words,
                item => _.max(item.data)
            )
        );
    }


    setFixLineHeights(event) {
        this.fixLineGraphHeights = event.target.checked;
        if (this.chart) {
            this.chartData = this.makeChartdata(this.data);
            this.chart.data = this.chartData;
            this.chart.update();
        }
    }

}
