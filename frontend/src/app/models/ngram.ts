import { Params } from '@angular/router';
import * as _ from 'lodash';

import { StoreSync } from '../store/store-sync';
import { Store } from '../store/types';

export type NgramMode = 'ngrams' | 'collocates';

export interface NgramSettings {
    mode: NgramMode,
    size: number;
    positions?: string;
    freqCompensation: boolean;
    analysis: string;
    maxDocuments: number;
    numberOfNgrams: number;
}

export class NgramParameters extends StoreSync<NgramSettings> {

    keysInStore = ['ngramSettings'];

    constructor(store: Store) {
        super(store);
        this.connectToStore();
    }

    stringifyNgramSettings(state: NgramSettings): string {
        return [
            `o:${state.mode == 'collocates' ? 'c' : 'n'}`,
            `s:${state.size}`,
            `p:${state.positions}`,
            `c:${state.freqCompensation}`,
            `a:${state.analysis}`,
            `m:${state.maxDocuments}`,
            `n:${state.numberOfNgrams}`
        ].join(',')
    }

    stateToStore(state: NgramSettings): Params {
        return { ngramSettings: this.stringifyNgramSettings(state)}
    }

    storeToState(params: Params): NgramSettings {
        if (_.has(params, 'ngramSettings')) {
            const stringComponents = params['ngramSettings'].split(',');
            return {
                mode: this.findSetting('o', stringComponents) === 'c' ? 'collocates' : 'ngrams',
                size: parseInt(this.findSetting('s', stringComponents), 10),
                positions: this.findSetting('p', stringComponents),
                freqCompensation: this.findSetting('c', stringComponents) === 'true',
                analysis: this.findSetting('a', stringComponents),
                maxDocuments: parseInt(this.findSetting('m', stringComponents), 10),
                numberOfNgrams: parseInt(this.findSetting('n', stringComponents), 10),
            }
        }
        return {
            mode: 'ngrams',
            size: 2,
            positions: 'any',
            freqCompensation: false,
            analysis: 'none',
            maxDocuments: 50,
            numberOfNgrams: 10,
        } as NgramSettings;
    }

    findSetting(abbreviation: string, stringComponents: string[]): string | undefined{
        const setting = stringComponents.find(s => s[0] === abbreviation);
        return setting?.split(':')[1];
    }
}
