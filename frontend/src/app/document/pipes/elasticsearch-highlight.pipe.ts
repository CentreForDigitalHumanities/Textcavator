import { Pipe, PipeTransform } from '@angular/core';
import * as _ from 'lodash';

import { CorpusField, FoundDocument } from '@models';

@Pipe({
    name: 'elasticsearchHighlight',
    standalone: false
})
export class ElasticsearchHighlightPipe implements PipeTransform {

    /**
     * Transforms a text to display highlights fetched from Elasticsearch
     *
     * @param document a FoundDocument, containing the fetched highlights
     */
    transform(content: string, field: CorpusField, document: FoundDocument) {
        if (_.isEmpty(content)) {
            return;
        }

        const highlighted = this.highlightedInnerHtml(content, field, document);
        return highlighted;
    }

    highlightedInnerHtml(content: string, field: CorpusField, document: FoundDocument) {;
        if (document.highlight && document.highlight.hasOwnProperty(field.name)) {
                for (const highlight of document.highlight[field.name]) {
                    const strippedHighlight = this.stripTags(highlight);
                    content = content.replace(strippedHighlight, highlight);
                }
            }
        return content;
    }

    stripTags(htmlString: string){
        const parseHTML= new DOMParser().parseFromString(htmlString, 'text/html');
        return parseHTML.body.textContent || '';
    }

}
