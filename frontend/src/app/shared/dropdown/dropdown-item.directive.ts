import { Directive, ElementRef, HostBinding, HostListener, Input, Output } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';
import { DropdownService } from './dropdown.service';
import * as _ from 'lodash';
import { NgbDropdownButtonItem, NgbDropdownItem } from '@ng-bootstrap/ng-bootstrap';

@Directive({
    selector: '[iaDropdownItem]',
    standalone: false,
    hostDirectives: [
        {
            directive: NgbDropdownItem,
            inputs: ['disabled: disabled'],
        },
        {
            directive: NgbDropdownButtonItem,
        }
    ],
})
export class DropdownItemDirective {
    @HostBinding('attr.role') role = 'option';
    @Input() value;

    @Output() onSelect = new Subject<any>();

    disabled: boolean;
    focused = new BehaviorSubject<boolean>(false);

    constructor(private elementRef: ElementRef, private dropdownService: DropdownService) { }

    @HostBinding('class.active')
    @HostBinding('attr.aria-selected')
    get isActive(): boolean {
        return _.isEqual(this.dropdownService.selection$.value, this.value);
    }

    @HostListener('focus')
    onFocus() {
        this.focused.next(true);
    }

    @HostListener('blur')
    onBlur() {
        this.focused.next(false);
    }

    @HostListener('click')
    @HostListener('keydown.enter')
    @HostListener('keydown.space')
    select() {
        if (!this.disabled) {
            this.onSelect.next(this.value);
            this.dropdownService.selection$.next(this.value);
            return false;
        }
    }

    @HostListener('keydown.arrowdown')
    navigateNext() {
        this.dropdownService.focusShift$.next(1);
        return false;
    }

    @HostListener('keydown.arrowup')
    navigatePrev() {
        this.dropdownService.focusShift$.next(-1);
        return false;
    }

    focus() {
        this.elementRef.nativeElement.focus();
    }
}
