import { Injectable } from '@angular/core';
import { BehaviorSubject, combineLatest, fromEvent, map, Observable, startWith } from 'rxjs';
import { setThemefaults } from 'app/visualization/chartjs-utils';
import { Chart } from 'chart.js';

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
        const query = window.matchMedia('(prefers-color-scheme: dark)');
        this.systemTheme$ = fromEvent<MediaQueryListEvent>(query, 'change').pipe(
            startWith(query),
            map(list => list.matches ? Theme.DARK : Theme.LIGHT)
        );
        this.theme$ = combineLatest([this.selection, this.systemTheme$]).pipe(
            map(([selection, system]) => selection || system)
        );
        this.theme$.subscribe((theme) => this.setTheme(theme));
    }

    setTheme(theme: Theme) {
        const root = (document.getRootNode() as Document).documentElement;
        root.setAttribute('data-theme', theme);
        setThemefaults(Chart.defaults);
    }
}
