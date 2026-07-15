import { Component, HostListener } from '@angular/core';
import { scrollIcons } from '../icons';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

@Component({
    selector: 'ia-back-to-top-button',
    templateUrl: './back-to-top-button.component.html',
    styleUrl: './back-to-top-button.component.scss',
    imports: [CommonModule, FontAwesomeModule],
})
export class BackToTopButton {
    isScrolledDown = false;
    icon = scrollIcons.top;

    @HostListener('window:scroll', [])
    @HostListener('window:resize', [])
    onScroll() {
        this.isScrolledDown = window.scrollY > screen.height;
    }

    scrollToTop() {
        window.scroll(0, 0);
        document.getElementById('main')?.focus()
    }
}
