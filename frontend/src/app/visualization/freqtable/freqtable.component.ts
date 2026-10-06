import { Input, Component, OnChanges, ViewEncapsulation, SimpleChanges } from '@angular/core';
import * as _ from 'lodash';
import { saveAs } from 'file-saver';
import { FreqTableHeaders } from '@models';
import { actionIcons, sortIcons } from '@shared/icons';
import { formatValue, getValue, transformWideFormat, wideFormatAvailable } from './freqtable-utils';
import { TablePaginator } from './paginator';

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

    tableData = new TablePaginator([], 20);

    wideFormatAvailable: boolean = false;
    format: 'long'|'wide' = 'long';

    fullTableToggle = false;
    disableFullTable = false;

    actionIcons = actionIcons;
    sortIcons = sortIcons;

    getValue = getValue;
    formatValue = formatValue;

    constructor() { }

    ngOnChanges(changes: SimpleChanges): void {
        this.checkWideFormat();
        this.checkFullTable();

        this.formatData();
    }

    checkWideFormat(): void {
        /** Checks whether wide format is available and assigns wideFormatColumn */
        this.wideFormatAvailable = wideFormatAvailable(this.headers);
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
            const [headers, data] = transformWideFormat(
                filteredData,
                this.headers,
            );
            this.formattedHeaders = headers;
            this.tableData.data$.next(data);
        } else if (this.fullTableToggle === true || this.headers === undefined) {  // also checks if no data is present to avoid error
            this.formattedHeaders = this.headers;
            this.tableData.data$.next(filteredData);
        } else {
            this.formattedHeaders = this.headers.filter(header => !header.isOptional);
            this.tableData.data$.next(filteredData);
        }

        if (this.formattedHeaders?.length) {
            this.tableData.sortBy$.next(this.formattedHeaders[0].key)
        }
    }

    parseTableData(): string[] {
        const data = this.tableData.data$.value.map(row => {
            const values = this.formattedHeaders.map(col => this.getValue(row, col, true));
            return  `${_.join(values, ',')}\n`;
        });
        data.unshift(`${_.join(this.formattedHeaders.map(col => col.label), ',')}\n`);
        return data;
    }

    downloadTable() {
        const data = this.parseTableData();
        const blob = new Blob(data, { type: `text/csv;charset=utf-8`, endings: 'native' });
        const filename = this.name + '.csv';
        saveAs(blob, filename);
    }
}
