import { fakeAsync, flushMicrotasks, TestBed } from '@angular/core/testing';
import { ApiService, CorpusService } from '@services';
import { CorpusDefinition } from './corpus-definition';
import { ApiServiceMock } from '@mock-data/api';
import { corpusDefinitionFactory } from '@mock-data/corpus-definition';
import * as _ from 'lodash';
import { corpusFactory, CorpusServiceMock } from '@mock-data/corpus';


describe('CorpusDefinition', () => {
    let apiService: ApiService;
    let corpusService: CorpusService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: ApiService, useClass: ApiServiceMock },
                { provide: CorpusService, useClass: CorpusServiceMock },
            ]
        });
        apiService = TestBed.inject(ApiService);
        corpusService = TestBed.inject(CorpusService);
    });

    it('should create for an existing corpus', () => {
        const corpus = new CorpusDefinition(apiService, corpusService, 1);
        expect(corpus).toBeTruthy();
        expect(corpus.id).toBe(1);
    });

    it('should create for a new corpus', () => {
        const corpus = new CorpusDefinition(apiService, corpusService);
        expect(corpus).toBeTruthy();
        expect(corpus.id).toBeUndefined();
    });

    it('should save updates', () => {
        const createSpy = spyOn(apiService, 'createCorpus').and.callThrough();
        const updateSpy = spyOn(apiService, 'updateCorpus').and.callThrough();

        const corpus = new CorpusDefinition(apiService, corpusService);
        corpus.definition = corpusDefinitionFactory();
        corpus.save();

        expect(createSpy).toHaveBeenCalledTimes(1);
        expect(updateSpy).not.toHaveBeenCalled();
        expect(corpus.id).toBeDefined();

        const newDefinition = _.set(corpusDefinitionFactory(), ['meta', 'title'], 'Different title');
        corpus.setFromDefinition(newDefinition);
        corpus.save();

        expect(createSpy).toHaveBeenCalledTimes(1);
        expect(updateSpy).toHaveBeenCalledTimes(1);
        expect(corpus.definition.meta.title).toBe('Different title');
    });

    it('should refresh searchable corpora', fakeAsync(() => {
        const spy = spyOn(corpusService, 'get').and.callThrough();

        // should not refresh when an inactive corpus is created
        const corpus = new CorpusDefinition(apiService, corpusService);
        corpus.definition = corpusDefinitionFactory();
        corpus.definition.name = 'my-new-corpus';// use unique name
        corpus.save();
        flushMicrotasks();
        expect(spy).not.toHaveBeenCalled();

        // should refresh when the corpus is activated
        corpus.active = true;
        corpus.save();
        flushMicrotasks();
        expect(spy).toHaveBeenCalledTimes(1);

        // update corpus data
        const newCorpus = corpusFactory();
        newCorpus.name = corpus.definition.name;
        corpusService.corporaPromise = Promise.resolve([
            newCorpus,
        ]);

        // should refresh when an active corpus is updated
        corpus.definition.meta.title = 'Fancy new title';
        corpus.save();
        flushMicrotasks();
        expect(spy).toHaveBeenCalledTimes(2);

        // should refresh when a cached corpus is deactivated
        corpus.active = false;
        corpus.save();
        flushMicrotasks();
        expect(spy).toHaveBeenCalledTimes(3);

        corpusService.corporaPromise = Promise.resolve([]);

        // should not refresh when an inactive corpus is updated
        corpus.definition.meta.title = 'Different title';
        corpus.save();
        flushMicrotasks();
        expect(spy).toHaveBeenCalledTimes(3);

    }));
});
