import { contentFieldFactory, corpusFactory } from '@mock-data/corpus';
import { ElasticsearchHighlightPipe } from './elasticsearch-highlight.pipe';
import { makeDocument } from '@mock-data/constructor-helpers';
import { highlightPostTag, highlightPreTag } from '@app/utils/es-query';

fdescribe('elasticsearchHighlightPipe', () => {
    const field = contentFieldFactory();
    let pipe: ElasticsearchHighlightPipe;

    beforeEach(() => {
        pipe = new ElasticsearchHighlightPipe();
    });

    it('should merge elasticsearch highlights', () => {
        let doc = makeDocument(
            { content: `Shall I compare thee to a summer’s day?
Thou art more lovely and more temperate:
Rough winds do shake the darling buds of May,
And summer’s lease hath all too short a date` },
            corpusFactory(),
            '18',
            0.5,
            { content: [
                `art more ${highlightPreTag}lovely${highlightPostTag} and more`,
                `shake the ${highlightPreTag}darling${highlightPostTag} buds of`,
            ]},
        );

        const result = pipe.transform(field, doc);
        expect(result).toBe(`Shall I compare thee to a summer’s day?
Thou art more ${highlightPreTag}lovely${highlightPostTag} and more temperate:
Rough winds do shake the ${highlightPreTag}darling${highlightPostTag} buds of May,
And summer’s lease hath all too short a date`);
    });
});
