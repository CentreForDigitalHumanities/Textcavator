import { Component, input, computed, effect, output } from '@angular/core';
import _ from 'lodash';
import { FormControl } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { padWithZero } from '@app/utils/utils';

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
        const checkedValue = _.min([_.max([selectedDate, this.minDate()]), this.maxDate()]);
        if (checkedValue) {
            this.onChange.emit(checkedValue);
        }
    }

    private string2Date(value: string): Date | null {
        return new Date(value);
    }

    private date2String(date: Date | null): string {
        if (!date) {
            return '';
        }
        const day = padWithZero(date.getDate(), 2);
        const month = padWithZero(date.getMonth() + 1, 2);
        const year = date.getFullYear();
        return `${year}-${month}-${day}`;
    }
}
