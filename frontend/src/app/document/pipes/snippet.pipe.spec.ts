import { sonnet } from './elasticsearch-highlight.pipe.spec';
import { SnippetPipe } from './snippet.pipe';

describe('SnippetPipe', () => {
    const pipe = new SnippetPipe();

    it('truncates long text', () => {
        expect(pipe.transform(sonnet[0], 20)).toBe('Shall I compare thee...');
    });

    it('leaves short text as-is', () => {
        const content = 'Shall I compare thee to a summer\'s day?';
        expect(pipe.transform(content, 50)).toEqual(content);
    });

    it('truncates array contents', () => {
        expect(pipe.transform(sonnet, 200)).toEqual([
`Shall I compare thee to a summer’s day?
Thou art more lovely and more temperate:
Rough winds do shake the darling buds of May,
And summer’s lease hath all too short a date:`,
`Sometime too hot the eye of...`,
        ])
    });
});
