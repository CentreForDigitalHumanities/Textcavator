/* eslint-disable @typescript-eslint/naming-convention */
import {
    Component,
    EventEmitter,
    Input,
    Output,
    OnDestroy,
    OnChanges,
    SimpleChanges,
    forwardRef,
    inject,
} from '@angular/core';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';
import * as _ from 'lodash';
import { actionIcons } from '../icons';
import { DropdownService } from './dropdown.service';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { NgbDropdown } from '@ng-bootstrap/ng-bootstrap';

/**
 * Wrapper around NgbDropdown for single-select fuctionality.
 *
 * Bootstrap dropdowns are general-purpose. The iaDropdown adds logic and roles
 * for a single-select combobox.
 *
 * For single-select form controls, you can also use `<select>`. The advantage
 * for the dropdown is that values can be of any data type (not just strings).
 * It also looks more consistent when mixed with other types of dropdowns (e.g.
 * multi-select).
 *
 * Example usage:
 *
 * ```html
 * <label id="label-lucky-number">Lucky number</label>
 * <ia-dropdown (onChange)="setLuckyNumber($event)">
 *     <button iaDropdownToggle aria-labelledby="label-lucky-number">
 *         {{luckyNumber}}
 *     </button>
 *     <div iaDropdownMenu>
 *         <button iaDropdownItem [value]="1">1</button>
 *         <button iaDropdownItem [value]="2">2</button>
 *     </div>
 * </iaDropdown>
 * ```
 *
 * Can be controlled with a [formControl], or with the [value] / (onChange) inputs.
 * Individual dropdown items also support a (onSelect) output event.
 *
 * The dropdown toggle is a form control that must be labelled, usually through
 * aria-labelledby.
 *
 * See also:
 * - https://ng-bootstrap.github.io/#/components/dropdown/examples
 * - https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/combobox_role
 * - https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/listbox_role
 */
@Component({
    selector: 'ia-dropdown',
    templateUrl: './dropdown.component.html',
    styleUrls: ['./dropdown.component.scss'],
    providers: [DropdownService,
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => DropdownComponent),
            multi: true,
        },
    ],
    hostDirectives: [
        NgbDropdown,
    ],
    host: {
        '(focusout)': 'blur$.next()',
        'class': 'd-block',
    },
    standalone: false
})
export class DropdownComponent<T> implements OnChanges, OnDestroy, ControlValueAccessor  {
    @Input() value: any;
    @Input() disabled: boolean;

    @Output()
    public onChange = new EventEmitter<T>();

    actionIcons = actionIcons;

    blur$ = new Subject<void>();

    private destroy$ = new Subject<void>();
    private onChangeSubscription?: Subscription;
    private onTouchedSubscription?: Subscription;

    private dropdownService = inject(DropdownService);

    constructor() {
        // don't trigger a lot of events when a user is quickly looping through the options
        // for example using the keyboard arrows
        this.dropdownService.selection$.pipe(
            takeUntil(this.destroy$),
            debounceTime(100),
            distinctUntilChanged(_.isEqual),
        ).subscribe((value) => this.onChange.next(value));
    }

    writeValue(value: any) {
        this.dropdownService.selection$.next(value);
    }

    registerOnChange(fn: any): void {
        this.onChangeSubscription?.unsubscribe();
        this.onChangeSubscription = this.dropdownService.selection$.subscribe(fn);
    }

    registerOnTouched(fn: any): void {
        this.onTouchedSubscription?.unsubscribe();
        this.onTouchedSubscription = this.blur$.subscribe(fn);
    }

    setDisabledState(isDisabled: boolean): void {
        this.disabled = isDisabled;
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.value) {
            this.dropdownService.selection$.next(this.value);
        }
        if (changes.disabled) {
            this.dropdownService.disabled$.next(this.disabled);
        }
    }

    ngOnDestroy(): void {
        this.blur$.complete();
        this.destroy$.next(undefined);
        this.destroy$.complete();
    }

}
