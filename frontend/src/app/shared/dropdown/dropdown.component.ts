/* eslint-disable @typescript-eslint/naming-convention */
import {
    Component,
    ElementRef,
    EventEmitter,
    Input,
    Output,
    OnDestroy,
    OnChanges,
    SimpleChanges,
    forwardRef,
    input,
    inject,
    ContentChild,
} from '@angular/core';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';
import * as _ from 'lodash';
import { actionIcons } from '../icons';
import { DropdownService } from './dropdown.service';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { NgbDropdown } from '@ng-bootstrap/ng-bootstrap';
import { DropdownToggleDirective } from './dropdown-toggle.directive';


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

    /** Removed, set aria-labelledby on iaDropdownToggle instead */
    @Input() labelledBy: string;

    @Output()
    public onChange = new EventEmitter<T>();

    @ContentChild(DropdownToggleDirective) trigger: ElementRef<HTMLButtonElement>;

    /** Removed, set [class] on iaDropdownToggle instead  */
    triggerClass = input<string>('');

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
