import { Component, HostListener } from '@angular/core';
import { scrollIcons } from '../icons';

@Component({
    selector: 'ia-back-to-top-button',
    standalone: false,
    templateUrl: './back-to-top-button.component.html',
    styleUrl: './back-to-top-button.component.scss'
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
