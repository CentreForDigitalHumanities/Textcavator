import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

import { CorpusService, NotificationService } from '../services/index';

@Injectable()
export class CorpusGuard {
    constructor(
        private notificationService: NotificationService,
        private corpusService: CorpusService,
        private authService: AuthService
    ) {}

    canActivate(
        next: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ): Observable<boolean> | Promise<boolean> | boolean {
        if (next.paramMap.has('corpus')) {
            return this.corpusService
                .set(next.paramMap.get('corpus'))
                .then((authorized) => {
                    if (!authorized) {
                        this.notificationService.showMessage(
                            'You do not have access to this corpus. Log in as an authorized user.',
                            'danger'
                        );
                        this.authService.showLogin(state.url);
                    }
                    return authorized;
                });
        }

        return false;
    }
}
