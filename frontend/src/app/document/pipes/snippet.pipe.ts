import { Pipe, PipeTransform } from '@angular/core';
@Pipe({
    name: 'snippet',
    standalone: false
})
export class SnippetPipe implements PipeTransform {

    /**
     * Transforms a text to only show its leading characters with an ellipsis
     *
     * @param nCharacters Specifies how many leading characters should be displayed
     */
    transform(text: string | string[], nCharacters=100) {
        if (Array.isArray(text)) {
            if (!text.length) {
                return text;
            }
            if (text[0].length >= nCharacters) {
                return [this.transform(text[0], nCharacters)];
            }
            return [text[0], ...this.transform(text.slice(1), nCharacters - text[0].length)];
        }

        if (text.length > nCharacters) {
            return text.slice(0, nCharacters).trimEnd().concat('...');
        } else {
            return text;
        }
    }

}
