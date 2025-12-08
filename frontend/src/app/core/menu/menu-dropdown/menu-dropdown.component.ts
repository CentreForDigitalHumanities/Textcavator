import { Component, DestroyRef, ElementRef, HostBinding, OnInit, ViewChild } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import _ from 'lodash';
import { BehaviorSubject, filter, fromEvent, merge, switchMap, take, timer } from 'rxjs';

let nextID = 0;

/**
 * component for navbar menu dropdown
 *
 * Use projected content to fill in the label and the menu items. E.g.
 *
 * ```html
 * <ia-menu-dropdown>
 *     <span iaMenuDropdownLabel>Example</span>
 *     <a class="navbar-item" [routerLink]="..." routerLinkActive="is-active">Item 1</a>
 *     <a class="navbar-item" [routerLink]="..." routerLinkActive="is-active">Item 2</a>
 * </ia-menu-dropdown>
 * ```
 */
@Component({
    selector: 'ia-menu-dropdown',
    standalone: false,
    templateUrl: './menu-dropdown.component.html',
    styleUrl: './menu-dropdown.component.scss'
})
export class MenuDropdownComponent implements OnInit {
    @HostBinding('class') class = 'navbar-item has-dropdown';
    @ViewChild('dropdownMenu') dropdownMenu: ElementRef;

    dropdownOpen$ = new BehaviorSubject<boolean>(false);
    id = nextID++;

    constructor(private destroyRef: DestroyRef) {}

    @HostBinding('class.is-active')
    get active(): boolean {
        return this.dropdownOpen$.value;
    }

    get dropdownID(): string {
        return `menu-dropdown-${this.id}`;
    }

    ngOnInit() {
        this.dropdownOpen$
            .pipe(takeUntilDestroyed(this.destroyRef), filter(_.identity))
            .subscribe(this.triggerCloseDropdown.bind(this));
    }

    toggleDropdown() {
        this.dropdownOpen$.next(!this.dropdownOpen$.value);
    }

    /** close dropdown when the user clicks or focuses elsewhere */
    private triggerCloseDropdown() {
        // observable of the next click
        // timer(0) is used to avoid the opening click event being registered
        const clicks$ = timer(0).pipe(
            switchMap(() => fromEvent(document, 'click'))
        );

        // observable of the dropdown losing focus

        const focusOutOfDropdown = (event: FocusEvent) =>
            _.isNull(event.relatedTarget) ||
            (event.relatedTarget as Element).parentElement.id !== this.dropdownID;

        const focusOut$ = fromEvent<FocusEvent>(
            this.dropdownMenu.nativeElement,
            'focusout'
        ).pipe(filter(focusOutOfDropdown));

        // when either of these happens, close the dropdown
        merge(clicks$, focusOut$).pipe(
            take(1),
            takeUntilDestroyed(this.destroyRef)
        ).subscribe(() => this.dropdownOpen$.next(false));
    }
 }
