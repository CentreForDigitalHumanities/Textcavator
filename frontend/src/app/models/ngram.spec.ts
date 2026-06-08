import { SimpleStore } from '../store/simple-store';
import { RouterStoreService } from '../store/router-store.service';
import { NgramParameters, NgramSettings } from './ngram';

describe('NgramParameters', ()=> {
    let store: RouterStoreService = new SimpleStore() as any;
    let ngramParameters: NgramParameters;
    const testState = {
        mode: 'ngrams',
        size: 3,
        positions: 'first',
        freqCompensation: true,
        analysis: 'clean',
        maxDocuments: 100,
        numberOfNgrams: 20,
    } as NgramSettings;
    const testParams = {ngramSettings: 'o:n,s:3,p:first,c:true,a:clean,m:100,n:20'}

    beforeEach(() => {
        ngramParameters = new NgramParameters(store);
    });

    it('should correctly convert internal state to a route parameter', () => {
        const params = ngramParameters.stateToStore(testState);
        expect(params).toEqual(testParams);
    });

    it('should correctly convert a route parameter to an internal state', () => {
        const state = ngramParameters.storeToState(testParams);
        expect(state).toEqual(testState);
    });

    it('should return default values if no relevant route parameter is present', () => {
        const defaultSettings = {
            mode: 'ngrams',
            size: 2,
            positions: 'any',
            freqCompensation: false,
            analysis: 'none',
            maxDocuments: 50,
            numberOfNgrams: 10,
        } as NgramSettings;
        const state = ngramParameters.storeToState({irrelevant: 'parameter'})
        expect(state).toEqual(defaultSettings);
    });

    it('should parse partial parameters', () => {
        const partialParams = {ngramSettings: 's:3,p:first,c:true,a:clean,m:100,n:20'};
        expect(ngramParameters.storeToState(partialParams)).toEqual(testState);

    });
});
