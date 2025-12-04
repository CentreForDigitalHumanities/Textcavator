import { Pipe, PipeTransform } from '@angular/core';

export const splitParagraphs = (content: string | string[]): string[] => {
    const paragraphs = typeof content === 'string' ? [content] : content;
    return paragraphs.filter(p => p !== '')
}

@Pipe({
    name: 'paragraph',
    standalone: false
})
export class ParagraphPipe implements PipeTransform {
    transform(content: string | string[]): string[] {
        return splitParagraphs(content);
    }
}
