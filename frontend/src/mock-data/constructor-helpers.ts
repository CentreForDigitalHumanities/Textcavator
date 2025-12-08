/* eslint-disable @typescript-eslint/naming-convention */
// these functions are shorthands to create objects that would normally come out the API

import { Corpus, FieldValues, FoundDocument, HighlightResult, SearchHit } from '../app/models';
import { corpusFactory } from './corpus';
import { TagServiceMock } from './tag';

const tagService = new TagServiceMock() as any;

export const exampleValues = {
    genre: 'Science Fiction',
    content: 'Bleep boop',
    date: '1800-01-01'
};

export const annotatedFieldValues = () => ({
    'content': 'Deze zomer kenmerkte zich door een gezegenden oogst, en met tevredenheid mocht de landbouwer deelnemen aan de Internationale Tentoonstelling die onlangs te Amsterdam, op uitstekende wijze ingericht, plaats had.',
    'content:ner': 'Deze zomer kenmerkte zich door een gezegenden oogst, en met tevredenheid mocht de landbouwer deelnemen aan de [Internationale Tentoonstelling](MISC) die onlangs te [Amsterdam](LOC), op uitstekende wijze ingericht, plaats had.',
    'person:ner-kw': null,
    'location:ner-kw': ['Amsterdam'],
    'organization:ner-kw': null,
    'miscellaneous:ner-kw': ['Internationale Tentoonstelling']
});

export const makeDocument = (
    fieldValues: FieldValues = exampleValues,
    corpus: Corpus = corpusFactory(),
    id: string = '0',
    relevance: number = 1,
    highlight: HighlightResult = undefined
): FoundDocument => {
    const hit: SearchHit = {
        _id: id, _score: relevance, _source: fieldValues, highlight
    };
    return new FoundDocument(tagService, corpus, hit);
};

