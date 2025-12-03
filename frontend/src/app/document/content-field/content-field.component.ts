import { Component, Input } from '@angular/core';
import { CorpusField, entityKeys, FoundDocument } from '@models';
import { splitParagraphs } from '../pipes/paragraph.pipe';
import { entityIcons } from '@app/shared/icons';
import _ from 'lodash';

@Component({
    selector: 'ia-content-field',
    templateUrl: './content-field.component.html',
    styleUrl: './content-field.component.scss',
    standalone: false
})
export class ContentFieldComponent {
    @Input() field: CorpusField;
    @Input() document: FoundDocument;
    @Input() showEntities: boolean;

    entityIcons = entityIcons;

    splitParagraphs = splitParagraphs;

    annotationName(annotation: string) {
        return _.get(entityKeys, annotation);
    }

    annotationIcon(annotation: string) {
        return _.get(entityIcons, this.annotationName(annotation));
    }
}
