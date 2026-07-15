import { Directive, effect, ElementRef, inject, input } from '@angular/core';

@Directive({
    selector: 'button[iaButtonLoading]',
    host: {
        // eslint-disable-next-line @typescript-eslint/naming-convention
        '[disabled]': 'iaButtonLoading()'
    }
})
export class ButtonLoadingDirective {
    iaButtonLoading = input<boolean>(false);
    private el = inject(ElementRef);

    constructor() {
        effect(() => {
            if (this.iaButtonLoading()) {
                this.showSpinner();
            } else {
                this.hideSpinner();
            }
        })
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
