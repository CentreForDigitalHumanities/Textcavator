import { hasPrefixTerm } from './query-utils';

describe('barchart query utils', () => {
    describe('hasPrefixTerm', () => {
        it('should match prefix queries', () => {
            const testCases: [string, boolean][] = [
                ['foo', false],
                ['foo*', true],
                ['foo* bar', true],
                ['(foo bar*) + baz', true],
            ];
            for (let [query, expected] of testCases) {
                expect(hasPrefixTerm(query)).toBe(expected);
            }
        });
    });
});
