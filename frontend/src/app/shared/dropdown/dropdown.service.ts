import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

@Injectable()
export class DropdownService {
    /** selected value */
    selection$ = new BehaviorSubject<any>(undefined);

    /** events where the user shifts focus through arrow navigation */
    focusShift$ = new Subject<number>();
};
