import { Injectable } from '@angular/core';
import { BehaviorSubject,  } from 'rxjs';

let nextID = 0;

@Injectable()
export class DropdownService {
    id = nextID++;

    /** selected value */
    selection$ = new BehaviorSubject<any>(undefined);

    disabled$ = new BehaviorSubject<boolean>(false);

    get triggerID(): string {
        return `dropdown-trigger-${this.id}`;
    }

    get menuID(): string {
        return `dropdown-menu-${this.id}`;
    }
};
