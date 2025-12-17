import { Pipe, PipeTransform } from '@angular/core';

const paragraphArray = (content: string | string[], splitText = false): string[] => {
    if (typeof content === 'string') {
        return splitText ? content.split('\n') : [content];
    } else {
        return content;
    }
}

export const splitParagraphs = (content: string | string[], splitText = false): string[] => {
    const paragraphs = paragraphArray(content, splitText);
    return paragraphs.filter(p => p !== '')
}

@Pipe({
    name: 'paragraph',
    standalone: false
})
export class ParagraphPipe implements PipeTransform {
    transform(content: string | string[], split = false): string[] {
        return splitParagraphs(content, split);
    }
}
