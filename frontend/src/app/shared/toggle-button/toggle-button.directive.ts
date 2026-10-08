import { computed, Directive, input } from '@angular/core';

@Directive({
    selector: 'button[iaToggleButton]',
    host: {
        // eslint-disable-next-line @typescript-eslint/naming-convention
        '[class]': 'classes()',
        // eslint-disable-next-line @typescript-eslint/naming-convention
        '[attr.aria-pressed]': 'active()'
    }
})
export class ToggleButtonDirective {
    active = input<boolean>(false);

    /** name of the CSS class that should be applied when active */
    activeClass = input<string>('btn-primary');

    /** name of the CSS class that should be applied when inactive */
    inactiveClass = input<string>('btn-body');

    classes = computed<Record<string, boolean>>(() => ({
        [this.activeClass()]: this.active(),
        [this.inactiveClass()]: !this.active(),
    }));
}
