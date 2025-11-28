import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { ReplaySubject } from 'rxjs';

export interface AlertConfig {
    message: string;
};


@Injectable({
    providedIn: 'root'
})
export class AlertService {
    alert$ = new ReplaySubject<AlertConfig>(1);

    constructor() {
        if (environment.showNamechangeAlert) {
            this.showNamechangeAlert();
        }
    }

    private showNamechangeAlert(): void {
        this.alert$.next({
            message:
                '"I-Analyzer" has been renamed, and is now called "Textcavator". Read more about this change on the about page.',
        });
    }
}
