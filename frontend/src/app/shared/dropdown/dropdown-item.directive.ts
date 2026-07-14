import { Directive, ElementRef, HostBinding, HostListener, Input, Output } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';
import { DropdownService } from './dropdown.service';
import * as _ from 'lodash';

@Directive({
    selector: '[iaDropdownItem]',
    standalone: false,
})
export class DropdownItemDirective {
    @HostBinding('class') class = 'dropdown-item';
    @HostBinding('attr.role') role = 'option';
    @HostBinding('attr.tabIndex') tabIndex = 0;

    @Input() value;

    @Input() disabled: boolean;

    @Output() onSelect = new Subject<any>();

    focused = new BehaviorSubject<boolean>(false);

    constructor(private elementRef: ElementRef, private dropdownService: DropdownService) { }

    /** value bound to [disabled] attribute in the DOM
     *
     * If `this.disabled === false`, the bound value is `undefined`
     *
     * This is bound to `disabled` attribute which is used as a CSS selector,
     * but that attribute is not supported for the menuitem role, so we also bind it
     * to `aria-disabled`. C.f. https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/menuitem_role
     */
    @HostBinding('attr.disabled')
    @HostBinding('attr.aria-disabled')
    get disabledAttribute() {
        if (this.disabled) {
            return true;
        };
    }

    @HostBinding('class.is-active')
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

    @HostListener('keydown.escape')
    close() {
        this.dropdownService.menuEscaped$.next();
        this.dropdownService.open$.next(false);
    }

    focus() {
        this.elementRef.nativeElement.focus();
    }
}
