import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { ReplaySubject } from 'rxjs';

export interface AlertConfig {
    message: string;
    onDismiss?: () => any;
    renderHtml?: boolean;
}

const nameChangeAlert = {
    message:
        '"I-Analyzer" has been renamed, and is now called "Textcavator". Read more about this change in <a href="https://github.com/CentreForDigitalHumanities/Textcavator/discussions/1958" target="_blank">this announcement on GitHub.</a>',
    onDismiss: () => localStorage.setItem('closedNameChangeAlert', 'true'),
    renderHtml: true,
};

@Injectable({
    providedIn: 'root',
})
export class AlertService {
    alert$ = new ReplaySubject<AlertConfig>(1);

    constructor() {
        this.showNamechangeAlert();
    }

    private showNamechangeAlert(): void {
        if (
            environment.showNamechangeAlert &&
            !localStorage.getItem('closedNameChangeAlert')
        ) {
            this.alert$.next(nameChangeAlert);
        }
    }
}
