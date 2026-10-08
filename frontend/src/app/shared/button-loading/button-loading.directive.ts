import { Directive, effect, ElementRef, inject, input, output } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { fromEvent } from 'rxjs';

@Directive({
    selector: 'button[iaButtonLoading]',
    host: {
        // eslint-disable-next-line @typescript-eslint/naming-convention
        '[attr.aria-disabled]': 'iaButtonLoading()',
    }
})
export class ButtonLoadingDirective {
    iaButtonLoading = input<boolean>(false);
    forwardClick = output<Event>({ alias: 'click' });
    private el = inject(ElementRef);

    constructor() {
        fromEvent(this.el.nativeElement, 'click', { capture: true }).pipe(
            takeUntilDestroyed(),
        ).subscribe(this.onClick.bind(this));

        effect(() => {
            if (this.iaButtonLoading()) {
                this.showSpinner();
            } else {
                this.hideSpinner();
            }
        })
    }

    onClick(event: Event) {
        event.stopPropagation();
        if (this.iaButtonLoading()) {
            event.preventDefault();
        } else {
            this.forwardClick.emit(event);

        }
    }

    showSpinner() {
        if (this.getSpinner()) {
            return;
        }

        const el = this.el.nativeElement as HTMLElement;
        const spinner = document.createElement('span');
        spinner.className = 'spinner-border spinner-border-sm me-2';
        spinner.setAttribute('aria-hidden', 'true');
        if (el.hasChildNodes()) {
            el.insertBefore(spinner, el.firstChild);
        } else {
            el.append(spinner);
        }
    }

    hideSpinner() {
        const spinner = this.getSpinner();
        if (spinner) {
            spinner.remove();
        }
    }

    getSpinner(): HTMLSpanElement | null {
        const el = this.el.nativeElement as HTMLElement;
        return el.querySelector('span.spinner-border');
    }
}
