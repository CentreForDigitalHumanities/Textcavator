import { Component, HostBinding, Input } from '@angular/core';
import { entityKeys } from '@app/models';
import { entityIcons } from '@app/shared/icons';
import _ from 'lodash';

@Component({
    selector: '[ia-annotated-content]',
    standalone: false,
    templateUrl: './annotated-content.component.html',
})
export class AnnotatedContentComponent {
    /** content with annotation in the text */
    @Input({ required: true }) content: string;

    @HostBinding('class') class = 'break-word';
    @HostBinding('style') style = 'white-space: pre-wrap;'

    entityIcons = entityIcons;

    annotationName(annotation: string) {
        return _.get(entityKeys, annotation);
    }

    annotationIcon(annotation: string) {
        return _.get(entityIcons, this.annotationName(annotation));
    }
}
