import { Component, DestroyRef, EventEmitter, Input, Output, SimpleChanges, Injectable } from '@angular/core';
import * as _ from 'lodash';
import { FormControl } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { formIcons } from '../icons';
import { NgbDateParserFormatter, NgbDateStruct } from '@ng-bootstrap/ng-bootstrap/datepicker';

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
        const dateString = [date.day, date.month, date.year].map((value) => String(value).padStart(2, '0'));
        return dateString.join(this.DELIMITER);
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
export class DatePickerComponent {
    @Input() value: Date | undefined;
    @Input() minDate: Date | undefined;
    @Input() maxDate: Date | undefined;
    @Input({ required: true }) default!: Date;
    @Input() unit: 'year' | 'date' = 'year';
    @Input() ariaLabel = 'date selector';
    @Output() onChange = new EventEmitter<Date>();

    control = new FormControl<Date | null>(null);

    formIcons = formIcons;

    constructor(private destroyRef: DestroyRef) { }

    get dateFormat(): string {
        return this.unit === 'year' ? 'yy' : 'dd-mm-yy';
    }

    ngOnInit() {
        this.control.valueChanges.pipe(
            takeUntilDestroyed(this.destroyRef)
        ).subscribe(() => this.onValueChange());
    }

    ngOnChanges(changes: SimpleChanges) {
        if (changes.value || changes.default) {
            this.control.setValue(this.value || this.default);
        }
    }

    onValueChange() {
        if (this.control.value) { // value is null when text input is invalid, e.g while typing
            const checkedValue = _.min([_.max([this.control.value, this.minDate]), this.maxDate]);
            this.onChange.emit(checkedValue);
        }
    }
}
