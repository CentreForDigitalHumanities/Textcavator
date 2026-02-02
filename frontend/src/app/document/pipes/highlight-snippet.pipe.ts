import { Pipe, PipeTransform } from '@angular/core';
import { highlightPostTag, highlightPreTag } from '@app/utils/es-query';

export interface HighlightSegment {
    content: string;
    highlight: boolean;
}

@Pipe({
    name: 'highlightSnippet',
    standalone: false,
})
export class HighlightSnippetPipe implements PipeTransform {

    transform(value: string): HighlightSegment[] {
        const start = value.indexOf(highlightPreTag);
        if (start >= 0) {
            const end = value.indexOf(highlightPostTag, start);
            if (end >= 0) {
                return [
                    { content: value.slice(0, start), highlight: false },
                    {
                        content: value.slice(start + highlightPreTag.length, end),
                        highlight: true
                    },
                    ...this.transform(value.slice(end + highlightPostTag.length))
                ];
            }
        }
        return [{content: value, highlight: false}]
    }

}
