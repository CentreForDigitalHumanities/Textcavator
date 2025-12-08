import { Pipe, PipeTransform } from '@angular/core';
import * as _ from 'lodash';

import { CorpusField, FoundDocument } from '@models';
import { highlightPostTag, highlightPreTag } from '@app/utils/es-query';

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
    transform(content: string | string[], field: CorpusField, document: FoundDocument) {
        if (_.isEmpty(content)) {
            return;
        }
        if (_.isArray(content)) {
            return content.map(item => this.highlightedInnerHtml(item, field, document));
        }
        return this.highlightedInnerHtml(content, field, document);
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

    stripTags(snippet: string){
        return snippet.replaceAll(highlightPreTag, '').replaceAll(highlightPostTag, '');
    }

}
