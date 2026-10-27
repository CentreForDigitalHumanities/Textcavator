import { Component, DestroyRef, EventEmitter, Input, Output, SimpleChanges, Injectable, OnChanges, OnInit } from '@angular/core';
import * as _ from 'lodash';
import { FormControl } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { formIcons } from '../icons';
import { NgbDateParserFormatter, NgbDateStruct } from '@ng-bootstrap/ng-bootstrap/datepicker';
import { padWithZero } from '@app/utils/utils';

@Injectable()
class IADateParserFormatter extends NgbDateParserFormatter {
    readonly DELIMITER = '-';

    parse(value: string): NgbDateStruct | null {
        if (!value) {
            return null;
        }
        const date = value.split(this.DELIMITER);
        return {
            day: parseInt(date[0], 10),
            month: parseInt(date[1], 10),
            year: parseInt(date[2], 10),
        };
    }

    format(date: NgbDateStruct | null): string {
        if (!date) {
            return '';
        }
        return [
            padWithZero(date.day, 2),
            padWithZero(date.month, 2),
            padWithZero(date.year, 4),
        ].join(this.DELIMITER);
    }
}

@Component({
    selector: 'ia-date-picker',
    templateUrl: './date-picker.component.html',
    styleUrls: ['./date-picker.component.scss'],
    providers: [
        { provide: NgbDateParserFormatter, useClass: IADateParserFormatter }
    ],
    standalone: false
})
export class DatePickerComponent implements OnInit, OnChanges {
    @Input() value: Date | undefined;
    @Input() minDate: Date | undefined;
    @Input() maxDate: Date | undefined;
    @Input({ required: true }) default!: Date;
    @Input() ariaLabel = 'date selector';
    @Output() onChange = new EventEmitter<Date>();

    control = new FormControl<NgbDateStruct | null>(null);

    formIcons = formIcons;

    constructor(private destroyRef: DestroyRef) { }

    get dateFormat(): string {
        return this.unit === 'year' ? 'yy' : 'dd-mm-yy';
    }

    get minDateStruct(): NgbDateStruct | null {
        return this.toNgbDateStruct(this.minDate);
    }

    get maxDateStruct(): NgbDateStruct | null {
        return this.toNgbDateStruct(this.maxDate);
    }

    ngOnInit() {
        const initialDate = this.value || this.default;
        this.control.setValue(this.toNgbDateStruct(initialDate));

        this.control.valueChanges.pipe(
            takeUntilDestroyed(this.destroyRef)
        ).subscribe(() => this.onValueChange());
    }

    ngOnChanges(changes: SimpleChanges) {
        if (changes.value || changes.default) {
            const newDate = this.value || this.default;
            this.control.setValue(this.toNgbDateStruct(newDate));
        }
    }

    onValueChange() {
        if (this.control.value) { // value is null when text input is invalid, e.g while typing
            const selectedDate = this.fromNgbDateStruct(this.control.value);
            const checkedValue = _.min([_.max([selectedDate, this.minDate]), this.maxDate]);
            this.onChange.emit(checkedValue);
        }
    }

    private fromNgbDateStruct(date: NgbDateStruct): Date {
        return new Date(date.year, date.month - 1, date.day);
    }

    private toNgbDateStruct(date: Date | undefined): NgbDateStruct | null {
        if (!date) {
            return null;
        }
        return {
            year: date.getFullYear(),
            month: date.getMonth() + 1,
            day: date.getDate(),
        };
    }


}
