import {
    Component,
    ElementRef,
    EventEmitter,
    Input,
    Output,
    OnDestroy,
    HostBinding,
    OnChanges,
    SimpleChanges,
    ViewChild,
    forwardRef,
    input,
} from '@angular/core';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';
import * as _ from 'lodash';
import { actionIcons } from '../icons';
import { DropdownService } from './dropdown.service';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { NgbDropdownToggle } from '@ng-bootstrap/ng-bootstrap';

let nextID = 0;

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
    standalone: false
})
export class DropdownComponent<T> implements OnChanges, OnDestroy, ControlValueAccessor  {
    @Input() value: any;
    @Input() disabled: boolean;

    /** ID of the element labelling the dropdown */
    @Input() labelledBy: string;

    @Output()
    public onChange = new EventEmitter<T>();

    @ViewChild(NgbDropdownToggle) trigger: ElementRef<HTMLButtonElement>;

    triggerClass = input<string>('');

    actionIcons = actionIcons;

    id = nextID++;

    private blur$ = new Subject<void>();
    private destroy$ = new Subject<void>();
    private onChangeSubscription?: Subscription;
    private onTouchedSubscription?: Subscription;

    constructor(private dropdownService: DropdownService) {
        // don't trigger a lot of events when a user is quickly looping through the options
        // for example using the keyboard arrows
        this.dropdownService.selection$.pipe(
            takeUntil(this.destroy$),
            debounceTime(100),
            distinctUntilChanged(_.isEqual),
        ).subscribe((value) => this.onChange.next(value));
    }

    get triggerID(): string {
        return `dropdown-trigger-${this.id}`;
    }

    get menuID(): string {
        return `dropdown-menu-${this.id}`;
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
    }

    ngOnDestroy(): void {
        this.blur$.complete();
        this.destroy$.next(undefined);
        this.destroy$.complete();
    }

    focusOnFirstItem(event: Event) {
        event.preventDefault();
        // focus on the first item - use setTimeout to wait until the menu is opened
        setTimeout(() => this.dropdownService.focusShift$.next(1));
    }

}
