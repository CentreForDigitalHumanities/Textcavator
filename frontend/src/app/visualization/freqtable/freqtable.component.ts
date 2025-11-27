import { Input, Component, OnChanges, OnDestroy, ViewEncapsulation, SimpleChanges } from '@angular/core';
import * as _ from 'lodash';
import { saveAs } from 'file-saver';
import { FreqTableHeader, FreqTableHeaders } from '@models';
import { actionIcons } from '@shared/icons';

@Component({
    selector: 'ia-freqtable',
    templateUrl: './freqtable.component.html',
    styleUrls: ['./freqtable.component.scss'],
    encapsulation: ViewEncapsulation.None,
    standalone: false
})
export class FreqtableComponent implements OnChanges {
    @Input() headers: FreqTableHeaders;
    @Input() data: any[];
    @Input() name: string; // name for CSV file
    @Input() defaultSort: string; // default field for sorting
    @Input() requiredColumn: string; // field required to include row in web view

    public defaultSortOrder = '-1';

    formattedHeaders: FreqTableHeaders;
    formattedData: any[];

    wideFormatColumn: number;
    format: 'long'|'wide' = 'long';

    fullTableToggle = false;
    disableFullTable = false;

    actionIcons = actionIcons;


    constructor() { }

    ngOnChanges(changes: SimpleChanges): void {
        this.checkWideFormat();
        this.checkFullTable();

        this.formatData();
    }

    checkWideFormat(): void {
        /** Checks whether wide format is available and assigns wideFormatColumn */

        if (this.headers && this.headers.find(header => header.isMainFactor)) {
            this.wideFormatColumn = _.range(this.headers.length)
                .find(index => this.headers[index].isMainFactor);
        } else {
            this.wideFormatColumn = undefined;
        }
    }

    /** Checks if full table is available. If so, it disables the full table switch.
     */
    checkFullTable(): void {
        if (this.headers && (this.headers.find(header => header.isOptional))) {
            this.disableFullTable = false;
        } else {
            this.disableFullTable = true;
        }
    }

    setFormat(format: 'long'|'wide'): void {
        this.format = format;
        this.formatData();
    }

    toggleFullTable() {
        this.fullTableToggle = !this.fullTableToggle;
        this.formatData();
    }

    formatData() {
        /** Formats the data in default (long) format, wide format, or fulltable format */

        let filteredData: any[];
        if (this.requiredColumn && this.data) {
            filteredData = this.data.filter(row => row[this.requiredColumn]);
        } else {
            filteredData = this.data;
        }

        if (this.format === 'wide') {
            const [headers, data] = this.transformWideFormat(filteredData);
            this.formattedHeaders = headers;
            this.formattedData = data;
        } else if (this.fullTableToggle === true || this.headers === undefined) {  // also checks if no data is present to avoid error
            this.formattedHeaders = this.headers;
            this.formattedData = filteredData;
        } else {
            this.formattedHeaders = this.headers.filter(header => !header.isOptional);
            this.formattedData = filteredData;
        }
    }

    transformWideFormat(data: any[]): [FreqTableHeaders, any[]] {
        const mainFactor = this.headers[this.wideFormatColumn];

        const mainFactorValues = _.uniqBy(
            data.map(row => row[mainFactor.key]),
            value => this.formatValue(value, mainFactor)
        );

        const newHeaders = this.wideFormatHeaders(mainFactor, mainFactorValues);

        // other factors
        const factorColumns = this.filterFactors(newHeaders);

        const newData = _.uniqBy(
            data,
            row => {
                const factorValues = factorColumns.map(column => this.getValue(row, column));
                return _.join(factorValues, '/');
            }
        );

        mainFactorValues.forEach(factorValue => {
            const filteredData = data.filter(row => this.getValue(row, mainFactor) === this.formatValue(factorValue, mainFactor));

            newData.forEach(newRow => {
                this.headers.forEach(header => {
                    if (! header.isSecondaryFactor) {
                        const key = this.wideFormatColumnKey(header, mainFactor, factorValue);

                        const rowData = filteredData.find(row =>
                            _.every(
                                factorColumns,
                                factor => this.getValue(row, factor) === this.getValue(newRow, factor)
                            )
                        );

                        if (rowData !== undefined) {
                            const value = rowData[header.key];
                            newRow[key] = value;
                        }
                    }
                });
            });
        });

        return [newHeaders, newData];
    }

    wideFormatHeaders(mainFactor: FreqTableHeader, factorValues: any[]) {
        const newLabel = (header: FreqTableHeader, factor: FreqTableHeader, factorValue) =>
            `${header.label} (${this.formatValue(factorValue, factor)})`;

        const otherHeaders = this.headers.filter((header, index) => header.key !== mainFactor.key);
        const newHeaders: FreqTableHeaders = _.flatMap(otherHeaders, header => {
            if (header.isSecondaryFactor) {
                // other factors are kept as-is
                return [header];
            } else {
                // for non-factor headers, make one column for each value of `mainFactor`
                return _.map(factorValues, value => (
                    {
                        label: newLabel(header, mainFactor, value),
                        key: this.wideFormatColumnKey(header, mainFactor, value),
                        format: header.format,
                        formatDownload: header.formatDownload,
                    } as FreqTableHeader
                ));
            }
        });

        return newHeaders;
    }

    wideFormatColumnKey(header: FreqTableHeader, mainFactor: FreqTableHeader, mainFactorValue): string {
        return `${header.key}###${this.formatValue(mainFactorValue, mainFactor)}`;
    }

    filterFactors(headers: FreqTableHeaders): FreqTableHeaders {
        return headers.filter(header => header.isSecondaryFactor);
    }

    parseTableData(): string[] {
        const data = this.formattedData.map(row => {
            const values = this.formattedHeaders.map(col => this.getValue(row, col, true));
            return  `${_.join(values, ',')}\n`;
        });
        data.unshift(`${_.join(this.formattedHeaders.map(col => col.label), ',')}\n`);
        return data;
    }

    getValue(row, column: FreqTableHeader, download = false) {
        return this.formatValue(row[column.key], column, download);
    }

    formatValue(value, column: FreqTableHeader, download = false) {
        if (download && column.formatDownload) {
            return column.formatDownload(value);
        }
        if (column.format) {
            return column.format(value);
        }
        return value;
    }

    downloadTable() {
        const data = this.parseTableData();
        const blob = new Blob(data, { type: `text/csv;charset=utf-8`, endings: 'native' });
        const filename = this.name + '.csv';
        saveAs(blob, filename);
    }
}
