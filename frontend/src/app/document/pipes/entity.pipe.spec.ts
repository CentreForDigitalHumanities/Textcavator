import { FieldEntities } from '@models';
import { EntityPipe } from './entity.pipe';

describe('EntityPipe', () => {
    const mockInput: Array<FieldEntities> = [
        {text: 'Nobody expects the ', entity: 'flat'},
        {text: 'Spanish Inquisition', entity: 'organization'},
        {text: '!', entity: 'flat'}
    ];

    it('creates an instance', () => {
       const pipe = new EntityPipe();
       expect(pipe).toBeTruthy();
    });

    it('adds mark tags to named entity annotations', ()=> {
        const pipe = new EntityPipe();
        const output = pipe.transform(mockInput.slice(1,2));
        expect(output).toContain('<mark ');
        expect(output).toContain('</mark>');
        expect(output).toContain('<svg ');
        expect(output).toContain('</svg>');
    });

    it('does not change Field Entities of `flat` type', () => {
        const pipe = new EntityPipe();
        const output = pipe.transform(mockInput.slice(0,1));
        expect(output).toEqual(mockInput[0].text);
    })

    it('concatenates highlighted and non-annotated text', () => {
        const pipe = new EntityPipe();
        const output = pipe.transform(mockInput);
        expect(typeof output).toBe('string');
    })
});
