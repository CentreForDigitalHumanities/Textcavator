import { Component, Input, OnChanges } from '@angular/core';
import * as _ from 'lodash';

import { entityIcons } from '@shared/icons';
import { entityKeys } from '@models';

@Component({
    selector: 'ia-entity-legend',
    templateUrl: './entity-legend.component.html',
    styleUrls: ['./entity-legend.component.scss'],
    standalone: false
})
export class EntityLegendComponent implements OnChanges {
    @Input() annotatedContent?: string;

    public entityIcons = entityIcons;
    public entities: string[] = ['person', 'location', 'organization', 'miscellaneous'];

    constructor() { }

    ngOnChanges(): void {
        this.entities = Object.values(entityKeys).filter(entityName => {
            const key = _.invert(entityKeys)[entityName]; // e.g. 'PER'
            const pattern = new RegExp(`\\[[^\\]]+\\]\\(${key}\\)`, 'g'); // e.g. '[William Shakespeare](PER)'
            return pattern.test(this.annotatedContent);
        });
    }

}
