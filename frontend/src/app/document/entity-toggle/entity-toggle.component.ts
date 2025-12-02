import { Component, output } from '@angular/core';

import { actionIcons } from '@shared/icons';
import { DialogService } from '@services';

@Component({
    selector: 'ia-entity-toggle',
    templateUrl: './entity-toggle.component.html',
    styleUrl: './entity-toggle.component.scss',
    standalone: false
})
export class EntityToggleComponent {
    actionIcons = actionIcons;
    toggleNER = output<Boolean>();
    toggleLabel: string;

    constructor(private dialogService: DialogService) {
        this.toggleLabel = 'ner-toggle';
    }

    public showNamedEntityDocumentation() {
        this.dialogService.showManualPage('namedentities');
    }
}
