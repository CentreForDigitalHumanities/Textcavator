import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';


@Injectable()
export class LoggedOnGuard  {
    constructor(private authService: AuthService) {}

    canActivate(
        next: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ): Observable<boolean> {
        if (this.authService.getCurrentUser()) {
            // A user is already present, no need to recheck
            return of(true);
        }
        return this.authService.checkUser().pipe(
            // In case no user is set, retry backend to obtain one
            // Redirect to login page if not successful
            map((userData) => !!userData),
            catchError(() => {
                this.authService.showLogin(state.url);
                return of(false);
            })
        );
    }
}
