import { DatePipe } from '@angular/common';
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'dateRange',
    standalone: false
})
export class DateRangePipe implements PipeTransform {
    constructor(
        private datePipe: DatePipe
    ) {}

    transform(value: string, ...args): string {
        const transformDate = (date) => this.datePipe.transform(date, ...args);
        if (value['gte'] == value['lte']) {
            return transformDate(value['gte']);
        }
        return `${transformDate(value['gte'])} - ${transformDate(value['lte'])}`
    }
}
