import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
@Pipe({
    name: 'snippet',
    standalone: false
})
export class SnippetPipe implements PipeTransform {
    constructor(private sanitizer: DomSanitizer) {
    }

    /**
     * Transforms a text to only show its leading characters with an ellipsis
     *
     * @param nCharacters Specifies how many leading characters should be displayed
     */
    transform(text: string | string[], nCharacters=100) {
        if (Array.isArray(text)) {
            text = text.join('\n\n');
        }

        if (text.length > nCharacters) {
            const snippedText = text.slice(0, nCharacters).concat('...');
            return this.sanitizer.bypassSecurityTrustHtml(snippedText);
        } else {
            return this.sanitizer.bypassSecurityTrustHtml(text);
        }
    }

}
