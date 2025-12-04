import { Pipe, PipeTransform } from '@angular/core';
import * as _ from 'lodash';

@Pipe({
    name: 'keyword',
    standalone: false
})
export class KeywordPipe implements PipeTransform {
    constructor() {}

    transform(content: string | string): string[] {
        if (_.isArray(content)) {
            return content;
        } else {
            return [content];
        }

    }

}
