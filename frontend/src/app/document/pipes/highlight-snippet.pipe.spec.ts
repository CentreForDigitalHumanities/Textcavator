import { highlightPostTag, highlightPreTag } from '@app/utils/es-query';
import { HighlightSnippetPipe } from './highlight-snippet.pipe';

describe('HighlightSnippetPipe', () => {
    let pipe: HighlightSnippetPipe;

    beforeEach(() => {
        pipe = new HighlightSnippetPipe();
    })

    it('creates segments', () => {
        const content = `To be or not to be, that is the ${highlightPreTag}question${highlightPostTag}.`;
        expect(pipe.transform(content)).toEqual([
            {
                content: 'To be or not to be, that is the ',
                highlight: false,
            }, {
                content: 'question',
                highlight: true,
            }, {
                content: '.',
                highlight: false,
            },
        ]);
    });

    it('finds multiple highlights', () => {
        const content = `To ${highlightPreTag}be${highlightPostTag} or not to ${highlightPreTag}be${highlightPostTag}, that is the question.`;
        expect(pipe.transform(content)).toEqual([
            {
                content: 'To ',
                highlight: false,
            }, {
                content: 'be',
                highlight: true,
            }, {
                content: ' or not to ',
                highlight: false,
            }, {
                content: 'be',
                highlight: true,
            }, {
                content: ', that is the question.',
                highlight: false,
            },
        ]);
    });

    it('handles input without highlights', () => {
        const content = 'To be or not to be, that is the question.';
        expect(pipe.transform(content)).toEqual([
            {
                content,
                highlight: false,
            }
        ]);
    });
});
