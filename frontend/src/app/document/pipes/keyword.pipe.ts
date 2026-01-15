import { Pipe, PipeTransform } from '@angular/core';
import * as _ from 'lodash';

@Pipe({
    name: 'keyword',
    standalone: false
})
export class KeywordPipe implements PipeTransform {
    constructor() {}

    transform(content: any): string[] {
        const items = _.isArray(content) ? content : [content];
        return items.map(String);
    }

}
