import { Injectable } from '@angular/core';
import { BehaviorSubject, combineLatest, fromEvent, map, Observable, startWith } from 'rxjs';
import { Chart } from 'chart.js';
import _ from 'lodash';

export enum Theme {
    DARK = 'dark',
    LIGHT = 'light',
}

@Injectable({
    providedIn: 'root'
})
export class ThemeService {
    selection = new BehaviorSubject<Theme | null>(null);
    systemTheme$: Observable<Theme>;
    theme$: Observable<Theme>;

    constructor(

    ) {
        this.selection.next(this.readStoredTheme());
        const query = window.matchMedia('(prefers-color-scheme: dark)');
        this.systemTheme$ = fromEvent<MediaQueryListEvent>(query, 'change').pipe(
            startWith(query),
            map(list => list.matches ? Theme.DARK : Theme.LIGHT)
        );
        this.theme$ = combineLatest([this.selection, this.systemTheme$]).pipe(
            map(([selection, system]) => selection || system)
        );
        this.selection.subscribe((theme) => this.writeStoredTheme(theme));
        this.theme$.subscribe((theme) => this.setTheme(theme));
    }

    setTheme(theme: Theme) {
        const root = (document.getRootNode() as Document).documentElement;
        root.setAttribute('data-theme', theme);
        this.setChartJSTheme();
    }

    setChartJSTheme() {
        const style = window.getComputedStyle(document.body);
        Chart.defaults.color = () => style.getPropertyValue('--bulma-text-strong');
        Chart.defaults.borderColor = () => style.getPropertyValue('--bulma-border');

        const active = _.values(Chart.instances);
        for (let chart of active) {
            chart.update();
        }
    }

    private readStoredTheme(): Theme | null {
        return (localStorage.getItem('theme') as Theme) || null;
    }

    private writeStoredTheme(theme: Theme | null): void {
        if (theme) {
            localStorage.setItem('theme', theme);
        } else {
            localStorage.removeItem('theme');
        }
    }
}
