import { contentFieldFactory, corpusFactory } from '@mock-data/corpus';
import { ElasticsearchHighlightPipe } from './elasticsearch-highlight.pipe';
import { makeDocument } from '@mock-data/constructor-helpers';
import { highlightPostTag, highlightPreTag } from '@app/utils/es-query';

const sonnet = [
`Shall I compare thee to a summer’s day?
Thou art more lovely and more temperate:
Rough winds do shake the darling buds of May,
And summer’s lease hath all too short a date:`,
`Sometime too hot the eye of heaven shines,
And often is his gold complexion dimm’d,
And every fair from fair sometime declines,
By chance, or nature’s changing course untrimm’d:`,
`But thy eternal summer shall not fade,
Nor lose possession of that fair thou ow’st,
Nor shall death brag thou wander’st in his shade,
When in eternal lines to time thou grow’st,`,
`    So long as men can breathe, or eyes can see,
    So long lives this, and this gives life to thee.`,
];

describe('elasticsearchHighlightPipe', () => {
    const field = contentFieldFactory();
    let pipe: ElasticsearchHighlightPipe;

    beforeEach(() => {
        pipe = new ElasticsearchHighlightPipe();
    });

    it('should merge elasticsearch highlights', () => {
        let doc = makeDocument(
            { content: sonnet[0] },
            corpusFactory(),
            '18',
            0.5,
            { content: [
                `art more ${highlightPreTag}lovely${highlightPostTag} and more`,
                `shake the ${highlightPreTag}darling${highlightPostTag} buds of`,
            ]},
        );

        const result = pipe.transform(doc.fieldValue(field), field, doc);
        expect(result).toBe(`Shall I compare thee to a summer’s day?
Thou art more ${highlightPreTag}lovely${highlightPostTag} and more temperate:
Rough winds do shake the ${highlightPreTag}darling${highlightPostTag} buds of May,
And summer’s lease hath all too short a date:`);
    });

    it('should work per paragraph', () => {
        let doc = makeDocument(
            { content: sonnet },
            corpusFactory(),
            '18',
            0.5,
            { content: [
                `Nor lose ${highlightPreTag}possession${highlightPostTag} of that`,
                `When in ${highlightPreTag}eternal lines${highlightPostTag} to time`,
            ]},
        );

        const result = pipe.transform(doc.fieldValue(field)[2], field, doc);
        expect(result).toBe(`But thy eternal summer shall not fade,
Nor lose ${highlightPreTag}possession${highlightPostTag} of that fair thou ow’st,
Nor shall death brag thou wander’st in his shade,
When in ${highlightPreTag}eternal lines${highlightPostTag} to time thou grow’st,`);
    });
});
