import { Component, input } from '@angular/core';

@Component({
    selector: '[ia-loading]',
    host: {
        // eslint-disable-next-line @typescript-eslint/naming-convention
        '[class.has-spinner-overlay]': 'iaLoading()',
    },
    template: `
        <ng-content></ng-content>
        @if (iaLoading()) {
            <div class="spinner-overlay text-center">
                <div class="spinner-border m-3"></div>
            </div>
        }
    `
})
export class LoadingComponent {
    iaLoading = input<boolean>(false, { alias: 'ia-loading'});
}
