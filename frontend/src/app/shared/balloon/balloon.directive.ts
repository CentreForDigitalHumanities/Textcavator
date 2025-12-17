import { Directive, ElementRef, Input, OnChanges } from '@angular/core';

/**
 * Directive for showing styled tooltip balloons.
 */
@Directive({
    selector: '[iaBalloon]',
    standalone: false
})
export class BalloonDirective implements OnChanges {
    @Input('iaBalloon')
    public text: string;

    @Input('iaBalloonPosition')
    public position: 'up' | 'left' | 'right' | 'down' | 'up-left' | 'up-right' | 'down-left' | 'down-right' = 'down';

    @Input('iaBalloonLength')
    public length: 'small' | 'medium' | 'large' | 'fit';

    /**
     * Show or hide the balloon, or show it on hover.
     */
    @Input('iaBalloonVisible')
    public visible: boolean | undefined;

    constructor(private el: ElementRef) {
    }

    ngOnChanges() {
        const element: HTMLElement = this.el.nativeElement;
        element.setAttribute('data-balloon', this.text);
        element.setAttribute('data-balloon-pos', this.position);
        element.setAttribute('data-balloon-length', this.length);
        if (this.visible) {
            element.setAttribute('data-balloon-visible', '');
            return;
        } else if (this.visible !== undefined || !this.text.length) {
            element.removeAttribute('data-balloon');
            element.removeAttribute('data-balloon-pos');
            element.removeAttribute('data-balloon-length');
        }

        element.removeAttribute('data-balloon-visible');
    }
}
