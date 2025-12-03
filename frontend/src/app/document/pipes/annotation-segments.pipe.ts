import { Pipe, PipeTransform } from '@angular/core';

export interface Segment {
    content: string;
    annotation?: string;
}

@Pipe({
    name: 'annotationSegments',
    standalone: false
})
export class AnnotationSegmentsPipe implements PipeTransform {

    transform(content: string): Segment[] {
        const pattern = /\[([^\]]+)\]\(([^\)]+)\)/g; // [annotatedText](annotation)
        const segments: Segment[] = [];
        let index = 0;

        for (let match of content.matchAll(pattern)) {
            const [matchedString, annotatedText, annotation] = match;
            segments.push({
                content: content.slice(index, match.index),
            });
            segments.push({
                content: annotatedText,
                annotation,
            });
            index = match.index + matchedString.length;
        }

        segments.push({
            content: content.slice(index, content.length),
        });

        return segments;
    }

}
