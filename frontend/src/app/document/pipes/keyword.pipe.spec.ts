import { KeywordPipe } from './keyword.pipe';

describe('KeywordPipe', () => {
    let pipe: KeywordPipe;

    beforeEach(() => {
        pipe = new KeywordPipe();
    })

    it('create an instance', () => {
        expect(pipe).toBeTruthy();
    });

    it('wraps single values in an array', () => {
        const input = 'Hello world!';
        const output = pipe.transform(input);
        expect(output).toEqual([input]);
    });

    it('returns arrays as-is', () => {
        const input = ['a', 'b', 'c'];
        const output = pipe.transform(input);
        expect(output).toEqual(input);
    });

    it('handles non-string source data', () => {
        // the pipe is meant for keyword fields, but should still handle non-string
        // values because we read field values from _source when displaying documents.
        // while the field is indexed as keyword, the source data may have been
        // int/bool/etc

        const input = 1;
        const output = pipe.transform(input);
        const expected = ['1'];
        expect(output).toEqual(expected);
    });

    it('handles arrays containing non-strings', () => {
        const input = [1, 'test', true];
        const output = pipe.transform(input);
        const expected = ['1', 'test', 'true'];
        expect(output).toEqual(expected);
    })
});
