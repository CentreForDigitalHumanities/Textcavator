import { Component, HostBinding, HostListener } from '@angular/core';
import { Theme, ThemeService } from '@services/theme.service';
import { themeIcons } from '@shared/icons';
import { modulo } from '@utils/utils';

@Component({
    selector: 'button[ia-theme-button]',
    template: `<span class="icon" aria-hidden="true">
        <fa-icon [icon]="currentOption.icon" />
    </span>`,
    standalone: false,
})
export class ThemeButtonComponent {
    options = [
        { label: 'system theme', icon: themeIcons.system, value: undefined },
        { label: 'light theme', icon: themeIcons.light, value: Theme.LIGHT },
        { label: 'dark theme', icon: themeIcons.dark, value: Theme.DARK },
    ];

    constructor(
        private themeService: ThemeService
    ) {}

    @HostBinding('attr.aria-label')
    get ariaLabel() {
        return this.currentOption.label;
    }

    get currentOption() {
        return this.options[this.currentIndex];
    }

    private get currentIndex(): number {
        return this.options.findIndex(
            option => option.value == this.themeService.selection.value
        );
    }

    @HostListener('click')
    cycle() {
        const nextIndex = modulo(this.currentIndex + 1, this.options.length);
        this.themeService.selection.next(this.options[nextIndex].value);
    }

}
