/* eslint-disable @typescript-eslint/naming-convention */
import { Directive, inject, input } from '@angular/core';
import { NgbDropdownToggle } from '@ng-bootstrap/ng-bootstrap';
import { DropdownService } from './dropdown.service';

@Directive({
    selector: '[iaDropdownToggle]',
    standalone: false,
    hostDirectives: [
        {
            directive: NgbDropdownToggle,
        }
    ],
    host: {
        'aria-haspopup': 'listbox',
        'role': 'combobox',
        'type': 'button',
        '[class]': 'class()',
        '[id]': 'dropdownService.triggerID',
        '[attr.aria-controls]': 'dropdownService.menuID',
        '[attr.disabled]': 'dropdownService.disabled$.value ? "" : null'
    }
})
export class DropdownToggleDirective {
    dropdownService = inject(DropdownService);

    class = input<string>('btn btn-body');
}
