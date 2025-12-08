import { TestBed, fakeAsync, waitForAsync } from '@angular/core/testing';
import * as _ from 'lodash';
import { reduce, take } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { exampleValues, makeDocument } from '@mock-data/constructor-helpers';
import { corpusFactory } from '@mock-data/corpus';
import { TagServiceMock, mockTags } from '@mock-data/tag';
import { FoundDocument } from './found-document';
import { TagService } from '@services/tag.service';
import { Tag } from './tag';


const maxScore = 2.9113607;
const mockResponse = {
    _index: 'test',
    _id: '12345',
    _score: 2.9113607,
    _source: {
        date: '1994-09-20',
        genre: 'Science fiction',
        content: 'You will rejoice to hear that no disaster has accompanied the ' +
            'commencement of an enterprise which you have regarded with such evil ' +
            'forebodings.'
    },
    highlight: {
        content: [
            '<em>rejoice</em>'
        ]
    }
};

describe('FoundDocument', () => {
    const mockTagService = new TagServiceMock() as any;
    const corpus = corpusFactory();

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: TagService, useClass: TagServiceMock },
            ]
        });
    });

    it('should construct from an elasticsearch response', () => {
        const document = new FoundDocument(
            mockTagService,
            corpus,
            mockResponse, maxScore
        );

        expect(document.id).toBe('12345');
        expect(document.fieldValues['genre']).toBe('Science fiction');
    });

    it('should reflect context', () => {
        const notDefinedInCorpus = makeDocument();
        expect(notDefinedInCorpus.hasContext).toBeFalse();

        const corpusWithContext = corpusFactory();
        corpusWithContext.documentContext = {
            contextFields: [corpusWithContext.fields[2]],
            displayName: 'date',
        }

        const missingValues = makeDocument(
            _.omit(exampleValues, ['date']),
            corpusWithContext
        );
        expect(missingValues.hasContext).toBeFalse();

        const shouldHaveContext = makeDocument(exampleValues, corpusWithContext);
        expect(shouldHaveContext.hasContext).toBeTrue();
    });

    it('should set tags', waitForAsync(() => {
        const doc = makeDocument({ great_field: 'test' });

        const tags$: Observable<Tag[][]> = doc.tags$.pipe(
            take(3),
            reduce(
                (accumulated, current) => [...accumulated, current],
                [],
            ),
        );

        const tag1 = _.first(mockTags);
        const tag2 = _.last(mockTags);

        doc.removeTag(tag1);
        doc.addTag(tag1);

        tags$.subscribe(allTags => {
            expect(allTags).toEqual([
                [tag1, tag2],
                [tag2],
                [tag1, tag2]
            ]);
        });
    }));

});
