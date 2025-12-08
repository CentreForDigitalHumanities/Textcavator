import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Params, Router } from '@angular/router';
import { BehaviorSubject, Observable, Subject, merge, of } from 'rxjs';
import { User } from '@models/index';
import { environment } from '@environments/environment';
import { AuthService } from '@services/auth.service';
import { filter, map } from 'rxjs/operators';
import { navIcons, userIcons } from '@shared/icons';

@Component({
    selector: 'ia-menu',
    templateUrl: './menu.component.html',
    styleUrls: ['./menu.component.scss'],
    standalone: false
})
export class MenuComponent implements OnDestroy, OnInit {
    brand = environment.navbarBrand;
    adminUrl = environment.adminUrl;

    menuOpen$ = new BehaviorSubject<boolean>(false);

    user$: Observable<User> = this.authService.currentUser$;

    route$: Observable<{
        url: string[];
        queryParams: Params;
    }>;

    navIcons = navIcons;
    userIcons = userIcons;

    private destroy$ = new Subject<void>();

    constructor(
        private authService: AuthService,
        private router: Router,
        private route: ActivatedRoute
    ) {}

    ngOnDestroy() {
        this.destroy$.next(undefined);
    }

    ngOnInit() {
        this.user$ = this.authService.currentUser$;
        this.makeRoute();
    }

    toggleMenu() {
        this.menuOpen$.next(!this.menuOpen$.value);
    }

    public async logout() {
        this.authService.logout(true).subscribe();
    }

    public async login() {
        this.authService.showLogin(this.router.url);
    }

    private makeRoute(): void {
        // observable that fires immediately, and after navigation
        const routeUpdates$ = merge(
            of(null),
            this.router.events.pipe(
                filter((event) => event instanceof NavigationEnd)
            )
        );

        this.route$ = routeUpdates$.pipe(
            map(() => this.route.firstChild?.snapshot),
            map((snapshot) => ({
                url: snapshot?.url.map((segment) => segment.path),
                queryParams: snapshot?.queryParams,
            }))
        );
    }
}
