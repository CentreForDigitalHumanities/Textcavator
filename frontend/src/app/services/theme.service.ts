import { Injectable } from '@angular/core';
import { BehaviorSubject, combineLatest, fromEvent, map, Observable, startWith } from 'rxjs';
import { Chart } from 'chart.js';
import _ from 'lodash';
import { environment } from '@environments/environment';

export enum Theme {
    DARK = 'dark',
    LIGHT = 'light',
}

@Injectable({
    providedIn: 'root'
})
export class ThemeService {
    /** Theme selection from the user.
     * `null` means no explicit preference, i.e. use  the system theme.
     */
    selection$ = new BehaviorSubject<Theme | null>(null);

    /** Theme used by the site */
    theme$: Observable<Theme>;

    /** Default dark/light preference from the browser/OS */
    private systemTheme$: Observable<Theme>;
    private storageKey = 'theme';

    constructor() {
        const initialSelection = environment.runInIFrame ? Theme.LIGHT : this.readStoredSelection();
        this.selection$.next(initialSelection);
        this.selection$.subscribe((theme) => this.storeSelection(theme));

        this.systemTheme$ = this.watchSystemTheme();
        this.theme$ = combineLatest([this.selection$, this.systemTheme$]).pipe(
            map(([selection, system]) => selection || system)
        );
        this.theme$.subscribe((theme) => this.applyTheme(theme));
    }

    private watchSystemTheme(): Observable<Theme> {
        const query = window.matchMedia('(prefers-color-scheme: dark)');
        return fromEvent<MediaQueryListEvent>(query, 'change').pipe(
            startWith(query),
            map(list => list.matches ? Theme.DARK : Theme.LIGHT)
        );
    }

    /** set theme in the site layout */
    private applyTheme(theme: Theme) {
        const root = (document.getRootNode() as Document).documentElement;
        root.setAttribute('data-theme', theme);
        this.applyChartJSTheme();
    }

    /** set chartjs defaults based on current style, and update active charts */
    private applyChartJSTheme() {
        const style = window.getComputedStyle(document.body);
        Chart.defaults.color = () => style.getPropertyValue('--bulma-text-strong');
        Chart.defaults.borderColor = () => style.getPropertyValue('--bulma-border');

        const active = _.values(Chart.instances);
        for (let chart of active) {
            chart.update();
        }
    }

    private readStoredSelection(): Theme | null {
        const value = localStorage.getItem(this.storageKey);
        if ([Theme.DARK, Theme.LIGHT].map(String).includes(value)) {
            return value as Theme;
        } else {
            return null;
        }
    }

    private storeSelection(theme: Theme | null): void {
        if (theme) {
            localStorage.setItem(this.storageKey, theme);
        } else {
            localStorage.removeItem(this.storageKey);
        }
    }
}
