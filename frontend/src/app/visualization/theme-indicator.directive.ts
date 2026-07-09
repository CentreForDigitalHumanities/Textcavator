import { DestroyRef, Directive, ElementRef, OnInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Theme, ThemeService } from '@services/theme.service';


/**
 * Lets the host element function as an indicator of the site theme (light/dark). The
 * element will set the theme as its value and fire an input event when the theme
 * changes.
 *
 * Can be used to let Vega visualisations observe the site theme. The element will be
 * hidden from the user.
 */
@Directive({
    selector: 'input[iaThemeIndicator]',
    standalone: false,
    host: { id: 'current-theme', hidden: '' }
})
export class ThemeIndicatorDirective implements OnInit {
    constructor(
        private themeService: ThemeService,
        private el: ElementRef,
        private destroyRef: DestroyRef,
    ) {}

    ngOnInit() {
        this.themeService.theme$.pipe(
            takeUntilDestroyed(this.destroyRef),
        ).subscribe(theme => this.setTheme(theme));
    }

    setTheme(theme: Theme) {
        const el = this.el.nativeElement as HTMLInputElement;
        el.value = theme;
        el.dispatchEvent(new Event('input'));
    }
}
