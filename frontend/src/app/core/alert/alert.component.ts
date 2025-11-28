import { Component, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AlertConfig, AlertService } from '@services/alert.service';
import _ from 'lodash';
import { BehaviorSubject, filter } from 'rxjs';

@Component({
    selector: 'ia-alert',
    standalone: false,
    templateUrl: './alert.component.html',
    styleUrl: './alert.component.scss',
})
export class AlertComponent {
    visible$ = new BehaviorSubject<boolean>(false);
    alertMessage$ = new BehaviorSubject<AlertConfig>(undefined);

    constructor(
        private alertService: AlertService,
        private destroyRef: DestroyRef
    ) {
        this.alertService.alert$
            .pipe(
                takeUntilDestroyed(this.destroyRef),
                filter(_.negate(_.isUndefined))
            )
            .subscribe({
                next: (config: AlertConfig) => this.showAlert(config),
            });
    }

    showAlert(message: AlertConfig): void {
        this.alertMessage$.next(message);
        this.visible$.next(true);
    }

    hideAlert(): void {
        this.alertMessage$.value.onDismiss?.();
        this.visible$.next(false);
        this.alertMessage$.next(undefined);
    }
}
