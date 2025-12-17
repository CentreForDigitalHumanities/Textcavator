import { annotatedFieldValues } from '@mock-data/constructor-helpers';
import { AnnotationSegmentsPipe } from './annotation-segments.pipe';

describe('AnnotationSegementsPipe', () => {
    let pipe: AnnotationSegmentsPipe;
    const values = annotatedFieldValues();

    beforeEach(() => {
       pipe = new AnnotationSegmentsPipe();
    });

    it('returns unannotated text as-is', () => {
        expect(pipe.transform(values.content)).toEqual([{ content: values.content }]);
    });

    it('extracts annotated segments', () => {
        expect(pipe.transform(values['content:ner'])).toEqual([
            {
                content:  'Deze zomer kenmerkte zich door een gezegenden oogst, en met tevredenheid mocht de landbouwer deelnemen aan de ',
            },
            {
                content: 'Internationale Tentoonstelling',
                annotation: 'MISC',
            },
            {
                content: ' die onlangs te ',
            },
            {
                content: 'Amsterdam',
                annotation: 'LOC',
            },
            {
                content: ', op uitstekende wijze ingericht, plaats had.',
            }
        ]);
    });
});
