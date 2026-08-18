import { CommonModule } from '@angular/common';
import { Component, computed, input, model } from '@angular/core';
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
    itemName = input.required<string>();
    limit = input<number>();

    input = '';
    inputConfirmKeys = ['Enter', ',', ';'];
    actionIcons = actionIcons;

    limitReached = computed(() => this.value().length >= (this.limit() ?? Infinity));

    handleInputKeydown(event: KeyboardEvent) {
        console.log(event);
        // confirm with enter/comma/semicolon
        if (this.inputConfirmKeys.includes(event.key)) {
            event.preventDefault();
            this.confirmInput();
        }
        // if input is empty, backspace removes last item
        if (event.key == 'Backspace' && !event.repeat && !this.input.length && this.value().length) {
            event.preventDefault();
            this.removeItem(this.value().length - 1);
        }
    }

    onBlur() {
        this.confirmInput();
    }

    confirmInput() {
        const input = this.input.trim();
        if (input.length) {
            this.value.update(value => _.uniq([...value, this.input]));
            this.input = '';
        }
    }

    removeItem(index: number) {
        this.value.update(value =>
            value.filter((_, i) => i !== index)
        );
    }
}
