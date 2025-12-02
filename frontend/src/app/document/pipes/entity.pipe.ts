import { Pipe, PipeTransform } from '@angular/core';
import { icon } from '@fortawesome/fontawesome-svg-core';

import { entityIcons } from '@shared/icons';
import { FieldEntities } from '@models';

@Pipe({
    name: 'entity',
    standalone: false
})
export class EntityPipe implements PipeTransform {
    /**
     * a pipe to transform a list of FieldEntities into flat text and entities
     * wrapped in <mark> tags, with icons indicating the type of named entity.
     * Note that this pipe needs to be followed by the | paragraph or | safeHtml pipe;
     * otherwise, the icons will be removed due to sanitization
     * @param entityArray: list of FieldEntities
     * @returns string of mixed text and html.
     */

    transform(entityArray: Array<FieldEntities>): string {
        const output = entityArray.map(ent => {
            if (ent.entity === 'flat') {
                return ent.text
            }
            else {
                const iconName = entityIcons[ent.entity];
                return `<mark class="entity-${ent.entity}" title="Named Entity ${ent.entity}">${ent.text} ${icon(iconName as any).html}</mark>`
            }
        })
        return output.join('');
    }

}
