import { Component, forwardRef, Input } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { ContentChange, QuillModules } from 'ngx-quill';
import { marked } from 'marked';
import TurndownService from 'turndown';

// functions to increase/decrease markdown header levels
// this is because section headers within documentation should be <h2> (<h1> is the page
// title), so users can create <h2>-<h6> in the editor, but the editor toolbar should
// not start counting at 2.

/** Increase markdown header levels; inserts a # before every header line. Does not
 * affect level 6 headers. */
export const increaseHeaderLevels = (content: string): string =>
    content.replace(/^#{1,5}\s/mg, '#$&');

/** Decrease markdown header levels; removes a # at the start of every header line. Does
 * not affect level 1 headers. */
export const decreaseHeaderLevels = (content: string): string =>
    content.replace(/^##/mg, '#');



@Component({
    selector: 'ia-markdown-editor',
    templateUrl: './markdown-editor.component.html',
    styleUrl: './markdown-editor.component.scss',
    standalone: false,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MarkdownEditorComponent),
            multi: true,
        },
    ],
})
export class MarkdownEditorComponent implements ControlValueAccessor {
    content: string = '';

    onChangeFn?: Function;
    onTouchedFn?: Function;

    modules: QuillModules = {
        toolbar: [
            ['bold', 'italic', 'underline', 'strike'],
            ['blockquote', 'code-block'],

            [{ header: 1 }, { header: 2 }],
            [{ list: 'ordered' }, { list: 'bullet' }],

            [{ header: [1, 2, 3, 4, 5, false] }],
            ['link', 'image'],

            ['clean'],
        ],
    };

    turndownService = new TurndownService({ headingStyle: 'atx' });

    writeValue(value: string): void {
        this.content = this.markdownToHtml(value);
    }

    registerOnChange(fn: Function): void {
        this.onChangeFn = fn;
    }

    registerOnTouched(fn: any): void {
        this.onTouchedFn = fn;
    }

    onChange(event: ContentChange) {
        if (this.onChangeFn) {
            const value = this.htmlToMarkdown(event.html);
            this.onChangeFn(value);
        }
    }

    onBlur() {
        if (this.onTouchedFn) {
            this.onTouchedFn();
        }
    }

    private markdownToHtml(value: string | null): string {
        if (value === null) {
            return '';
        }
        const headersAdjusted = decreaseHeaderLevels(value);
        const html = marked.parse(headersAdjusted, { async: false });
        return html;
    }

    private htmlToMarkdown(value: string | null): string {
        if (value === null) {
            return '';
        }
        const markdown = this.turndownService.turndown(value);
        const headersAdjusted = increaseHeaderLevels(markdown);
        return headersAdjusted;
    }
}
