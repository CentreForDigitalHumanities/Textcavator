import { Component, DestroyRef, EventEmitter, Input, Output, SimpleChanges } from '@angular/core';
import * as _ from 'lodash';
import { FormControl } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
    selector: 'ia-date-picker',
    templateUrl: './date-picker.component.html',
    styleUrls: ['./date-picker.component.scss'],
    standalone: false
})
export class DatePickerComponent {
    @Input() value: Date;
    @Input() minDate: Date;
    @Input() maxDate: Date;
    @Input({ required: true }) default!: Date;
    @Input() unit: 'year'|'date' = 'year';
    @Input() ariaLabel: string;
    @Output() onChange = new EventEmitter<Date>();

    control = new FormControl<Date>(null);

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
