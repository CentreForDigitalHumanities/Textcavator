import { Component, HostBinding, Input } from '@angular/core';

@Component({
    selector: '[ia-highlighted-content]',
    templateUrl: './highlighted-content.component.html',
    standalone: false,
})
export class HighlightedContentComponent {
    /** content with highlights */
    @Input({ required: true }) content: string;

    @HostBinding('class') class = 'break-word';
    @HostBinding('style') style = 'white-space: pre-wrap;'
}
