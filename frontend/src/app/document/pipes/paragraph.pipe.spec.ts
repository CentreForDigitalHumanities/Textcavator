import { ParagraphPipe } from './paragraph.pipe';

describe('ParagraphPipe', () => {
    let pipe: ParagraphPipe;

    beforeEach(() => {
        pipe = new ParagraphPipe();
    })

    it('creates an instance', () => {
        expect(pipe).toBeTruthy();
    });

    it('does not split text without linebreaks', () => {
        const input = 'Some text. And some more text. And even more.';
        const output = pipe.transform(input);
        expect(output).toEqual([input]);
    });

    it('splits single linebreaks', () => {
        const input = 'Some text.\nAnd some more text.\nAnd even more.';
        const output = pipe.transform(input, true);
        const expected = ['Some text.', 'And some more text.', 'And even more.'];
        expect(output).toEqual(expected);
    });

    it('splits multiple linebreaks', () => {
        const input = '\nSome text.\n\n\nAnd some more text.\n\n';
        const output = pipe.transform(input, true);
        const expected = ['Some text.', 'And some more text.']
        expect(output).toEqual(expected);
    });

    it('does not modify content which is already split', () => {
        const input = ['Some text.', 'And some more.'];
        const output = pipe.transform(input);
        expect(output).toEqual(input);
    })
});
