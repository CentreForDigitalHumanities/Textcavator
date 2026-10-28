import { Component, Injectable, input, computed, effect, output } from '@angular/core';
import _ from 'lodash';
import { FormControl } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
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
export class DatePickerComponent {
    value = input<Date | undefined>(undefined);
    minDate = input<Date | undefined>(undefined);
    maxDate = input<Date | undefined>(undefined);
    default = input.required<Date>();
    ariaLabel = input<string>('date selector');
    onChange = output<Date>();

    // The type is string when the user manually types an invalid date string.
    control = new FormControl<NgbDateStruct | string | null>(null, {
        nonNullable: true,
    });
    formIcons = formIcons;

    minDateStruct = computed(() => this.toNgbDateStruct(this.minDate()));
    maxDateStruct = computed(() => this.toNgbDateStruct(this.maxDate()));

    controlValue = toSignal(this.control.valueChanges, {
        initialValue: this.control.value,
    });

    constructor() {
        effect(() => {
            const newDate = this.value() || this.default();
            this.control.setValue(this.toNgbDateStruct(newDate));
        });

        effect(() => {
            const value = this.controlValue();
            if (value) {
                this.onValueChange();
            }
        });
    }

    private onValueChange(): void {
        if (typeof this.control.value === 'string') {
            return;
        }
        const selectedDate = this.fromNgbDateStruct(this.control.value);
        const checkedValue = _.min([_.max([selectedDate, this.minDate()]), this.maxDate()]);
        this.onChange.emit(checkedValue);
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
