/* eslint-disable @typescript-eslint/naming-convention */
import {  Directive, inject } from '@angular/core';
import { DropdownService } from './dropdown.service';
import { NgbDropdownMenu } from '@ng-bootstrap/ng-bootstrap';

@Directive({
    selector: '[iaDropdownMenu]',
    standalone: false,
    hostDirectives: [
        {
            directive: NgbDropdownMenu,
        }
    ],
    host: {
        'role': 'listbox',
        '[id]': 'dropdownService.menuID',
    }
})
export class DropdownMenuDirective {
    dropdownService = inject(DropdownService);
}
