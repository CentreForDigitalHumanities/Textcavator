import { Component, input, computed, effect, output } from '@angular/core';
import _ from 'lodash';
import { FormControl } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import moment from 'moment';

@Component({
    selector: 'ia-date-picker',
    templateUrl: './date-picker.component.html',
    styleUrls: ['./date-picker.component.scss'],
    standalone: false
})
export class DatePickerComponent {
    value = input<Date | undefined>(undefined);
    minDate = input<Date | undefined>(undefined);
    maxDate = input<Date | undefined>(undefined);
    default = input.required<Date>();
    ariaLabel = input<string>('date selector');
    onChange = output<Date>();

    control = new FormControl<string>('', {
        nonNullable: true,
    });

    minDateString = computed(() => this.date2String(this.minDate() ?? null));
    maxDateString = computed(() => this.date2String(this.maxDate() ?? null));

    controlValue = toSignal(this.control.valueChanges, {
        initialValue: this.control.value,
    });

    constructor() {
        effect(() => {
            const newDate = this.value() || this.default();
            this.control.setValue(this.date2String(newDate), { emitEvent: false });
        });

        effect(() => {
            const value = this.controlValue();
            if (value) {
                this.onValueChange();
            }
        });
    }

    private onValueChange(): void {
        const value = this.control.value;
        if (!value) {
            return;
        }
        const selectedDate = this.string2Date(value);
        const minDate = this.minDate();
        const maxDate = this.maxDate();

        let checkedValue = moment(selectedDate);

        if (minDate) {
            checkedValue = moment.max(checkedValue, moment(minDate));
        }
        if (maxDate) {
            checkedValue = moment.min(checkedValue, moment(maxDate));
        }

        if (checkedValue) {
            this.control.setValue(this.date2String(checkedValue.toDate()), { emitEvent: false });
            this.onChange.emit(checkedValue.toDate());
        }
    }

    private string2Date(value: string): Date | null {
        return new Date(value);
    }

    private date2String(date: Date | null): string {
        return date ? moment(date).format('YYYY-MM-DD') : '';
    }
}
