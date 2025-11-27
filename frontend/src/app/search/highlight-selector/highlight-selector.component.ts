import { Component, Input } from '@angular/core';
import { actionIcons } from '@shared/icons';
import { DEFAULT_HIGHLIGHT_SIZE, PageResults } from '@models/page-results';
import { Observable } from 'rxjs';
import * as _ from 'lodash';


@Component({
    selector: 'ia-highlight-selector',
    templateUrl: './highlight-selector.component.html',
    styleUrls: ['./highlight-selector.component.scss'],
    standalone: false
})
export class HighlightSelectorComponent {
    @Input() pageResults: PageResults;

    actionIcons = actionIcons;

    constructor() {
    }

    get highlight$(): Observable<number|undefined> {
        return this.pageResults?.highlight$;
    }

    get highlight(): number|undefined {
        return this.pageResults?.state$.value.highlight;
    }

    updateHighlightSize(instruction?: string) {
        const currentValue = this.pageResults.state$.value.highlight || DEFAULT_HIGHLIGHT_SIZE;
        let newValue: number|undefined;
        if (instruction === 'on') {
            newValue = DEFAULT_HIGHLIGHT_SIZE;
        } else if (instruction === 'more' && currentValue < 800) {
            newValue = currentValue + 200;
        } else if (instruction === 'less' && currentValue > 200) {
            newValue = currentValue - 200;
        } else if (instruction === 'off') {
            newValue = undefined;
        }
        this.pageResults.setParams({ highlight: newValue });
    }

}
