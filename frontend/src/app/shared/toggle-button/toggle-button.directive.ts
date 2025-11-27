import { Directive, HostBinding, Input } from '@angular/core';

@Directive({
    selector: 'button[iaToggleButton]',
    standalone: false
})
export class ToggleButtonDirective {
    @HostBinding('attr.aria-pressed')
    @Input() active: boolean;

    /** name of the CSS class that should be applied when active */
    @Input() activeClass: string = 'is-primary';

    @HostBinding('class')
    get classes(): Record<string, boolean> {
        return { [this.activeClass]: this.active }
    }
}
