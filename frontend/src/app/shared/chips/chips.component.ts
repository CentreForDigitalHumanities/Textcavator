import { CommonModule } from '@angular/common';
import { Component, input, model } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { actionIcons } from '../icons';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import _ from 'lodash';

@Component({
    selector: 'ia-chips',
    imports: [CommonModule, FormsModule, FontAwesomeModule],
    templateUrl: './chips.component.html',
    styleUrl: './chips.component.scss',
    host: {
        class: 'form-control px-2 py-1',
        // eslint-disable-next-line @typescript-eslint/naming-convention
        '(focusout)': 'onBlur()',
    },
})
export class ChipsComponent {
    value = model<string[]>([]);
    input = '';
    inputAriaLabel = input.required<string>();

    inputConfirmKeys = ['Enter', ',', ';'];
    actionIcons = actionIcons;

    handleInputKeydown(event: KeyboardEvent) {
        if (this.inputConfirmKeys.includes(event.key)) {
            event.preventDefault();
            this.confirmInput();
        }
    }

    onBlur() {
        this.confirmInput();
    }

    confirmInput() {
        if (this.input.length) {
            this.value.update(value => _.uniq([...value, this.input]));
            this.input = '';
        }
    }
}
