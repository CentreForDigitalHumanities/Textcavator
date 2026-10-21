import { Directive, effect, ElementRef, inject, input } from '@angular/core';

@Directive({
    selector: '[iaLoading]',
    host: {
        // eslint-disable-next-line @typescript-eslint/naming-convention
        '[class.has-spinner-overlay]': 'iaLoading()',
    }
})
export class LoadingDirective {
    iaLoading = input<boolean>(false);
    private el = inject(ElementRef);

    constructor() {
        effect(() => {
            if (this.iaLoading()) {
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
        const overlay = document.createElement('div');
        overlay.className = 'spinner-overlay text-center';
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border m-3';
        overlay.appendChild(spinner);
        el.append(overlay);
    }

    hideSpinner() {
        const spinner = this.getSpinner();
        if (spinner) {
            spinner.remove();
        }
    }

    getSpinner(): HTMLSpanElement | null {
        const el = this.el.nativeElement as HTMLElement;
        return el.querySelector('div.spinner-overlay');
    }

}
