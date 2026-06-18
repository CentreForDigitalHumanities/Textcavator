import { Params } from '@angular/router';
import * as _ from 'lodash';

import { StoreSync } from '../store/store-sync';
import { Store } from '../store/types';

export type NgramMode = 'ngrams' | 'collocates';

export type FreqMode = 'absolute' | 'legacy' | 'pmi';

export interface NgramSettings {
    mode: NgramMode,
    size: number;
    positions?: string;
    freqCompensation: FreqMode;
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
        const parsed = this.parseParamString(_.get(params, 'ngramSettings', ''));
        return {
            mode: _.get(parsed, 'o') === 'c' ? 'collocates' : 'ngrams',
            size: this.parseInt(_.get(parsed, 's'), 2),
            positions: _.get(parsed, 'p', 'any'),
            freqCompensation: this.parseFreqCompenstation(_.get(parsed, 'c', '')),
            analysis: _.get(parsed, 'a', 'none'),
            maxDocuments: this.parseInt(_.get(parsed, 'm'), 50),
            numberOfNgrams: this.parseInt(_.get(parsed, 'n'), 10),
        }
    }

    private parseParamString(value: string): Record<string, string> {
        const pairs = value.split(',').map(part => part.split(':', 2))
        return _.fromPairs(pairs);
    }

    private parseInt(value: string | undefined, defaultValue: number): number {
        const parsed = parseInt(value ?? '', 10);
        return _.isNaN(parsed) ? defaultValue : parsed;
    }

    private parseFreqCompenstation(value: string): FreqMode {
        const keys: Record<string, FreqMode> = {
            'true': 'legacy',
            'false': 'absolute',
            'abs': 'absolute',
            'leg': 'legacy',
            'pmi': 'pmi'
        }
        return _.get(keys, value, 'absolute')
    }
}
