import { makeDocument } from '@mock-data/constructor-helpers';
import { corpusFactory, intFieldFactory } from '@mock-data/corpus';
import { makeContextParams } from './document-context';

describe('document context utils', () => {
    const corpus = corpusFactory();
    corpus.fields.push(intFieldFactory());
    corpus.documentContext = {
        contextFields: [corpus.fields[2]],
        displayName: 'date',
        sortField: corpus.fields[3],
        sortDirection: 'asc',
    }

    const document = makeDocument();

    it('should create a document context link', () => {
        const params = makeContextParams(document, corpus);
        expect(params).toEqual({
            date: '1800-01-01:1800-01-01',
            sort: 'page,asc'
        });
    });
});
