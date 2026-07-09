import { Params } from '@angular/router';
import { StoreSync } from '../store/store-sync';
import { CorpusField } from './corpus';
import { Store } from '../store/types';
import { QueryModel } from './query';
import { findByName } from '@utils/utils';
import * as _ from 'lodash';
import { Observable, merge, of, timer } from 'rxjs';
import { map, takeUntil } from 'rxjs/operators';

export interface VisualizationSelection {
    name: string;
    field: CorpusField;
}

export interface VisualizationOption {
    name: string;
    label: string;
    fields: CorpusField[];
    disabled$: Observable<boolean>;
}

const REQUIRE_SEARCH_TERM = ['termfrequency', 'ngram'];

const DISPLAY_NAMES = {
    resultscount: 'Number of results',
    termfrequency: 'Frequency of the search term',
    ngram: 'Neighbouring words',
    wordcloud: 'Most frequent words',
    map: 'Map of locations',
};

export class VisualizationSelector extends StoreSync<VisualizationSelection | null> {
    options: VisualizationOption[];
    activeOption$: Observable<VisualizationOption>;

    defaultState: VisualizationSelection | null;

    protected keysInStore = ['visualize', 'visualizedField'];

    constructor(
        store: Store,
        public query: QueryModel,
    ) {
        super(store);
        this.options = this.getVisualizationOptions(this.query);
        this.defaultState = this.getDefaultOption(this.options, this.query);
        this.connectToStore(true);
        this.activeOption$ = this.state$.pipe(
            map(this.activeOption.bind(this))
        );

        this.query.update.pipe(
            takeUntil(this.complete$)
        ).subscribe(() => this.checkActiveOption());
    }

    /**
     * set the visualisation type.
     *
     * preserves the visualisation field, unless it is not available for the
     * given visualisation.
     */
    setVisualizationType(name: string) {
        const selection = findByName(this.options, name);
        const currentField = this.state$.value.field;
        if (selection.fields.includes(currentField)) {
            this.setParams({name});
        } else {
            this.setParams({name, field: selection.fields[0]});
        }
    }

    /** set the visualised corpus field.
     *
     * preserves the visualisation type, unless it is not available for the
     * given field.
     */
    setVisualizedField(field: CorpusField) {
        const currentVisualisation = this.state$.value.name;

        if (field.visualizations.includes(currentVisualisation)) {
            this.setParams({field});
        } else {
            this.setParams({field, name: field.visualizations[0]});
        }
    }

    protected stateToStore(state: VisualizationSelection | null): Params {
        if (!state) {
            return { visualize: null, visualizedField: null };
        }
        return {
            visualize: state.name || null,
            visualizedField: state.field?.name || null,
        };
    }

    protected storeToState(params: Params): VisualizationSelection | null {
        const name = params['visualize'];

        if (name) {
            const fieldName = params['visualizedField'];
            const field = findByName(this.query.corpus.fields, fieldName);
            return { name, field };
        } else {
            return this.defaultState;
        }
    }

    /**
     * generates a list of options for visualisation types.
     */
    private getVisualizationOptions(query: QueryModel): VisualizationOption[] {
        const hasVisualizations = (field: CorpusField) => field.visualizations?.length;

        const fields = query.corpus.fields.filter(hasVisualizations);
        const names = _.uniq(
            _.flatMap(fields, field => field.visualizations)
        );

        return names.map(name => {
            const label = DISPLAY_NAMES[name];
            const filteredFields = fields.filter(field => field.visualizations.includes(name));
            const disabled$ = this.disabled$(name, query);
            return {
                name,
                label,
                fields: filteredFields,
                disabled$,
            };
        });
    }

    /**
     * observable of when the given visualisation type should be disabled
     * based on the query state.
     */
    private disabled$(name: string, query: QueryModel): Observable<boolean> {
        const now = timer(0);
        const updates = merge(now, query.update);
        return updates.pipe(
            map(() => this.disabled(name, query)),
        );
    }

    /** whether the given visualisation type should be disabled based on the
     * _current_ query state.
     */
    private disabled(name: string, query: QueryModel): boolean {
        if (REQUIRE_SEARCH_TERM.includes(name)) {
            return _.isEmpty(query.queryText);
        } else {
            return false;
        }
    }

    /** returns the default state for the visualisation selector.
     *
     * filters the pre-generated list of options based on the query state,
     * and picks the first enabled option.
     */
    private getDefaultOption(
        options: VisualizationOption[], query: QueryModel
    ): VisualizationSelection | null {
        const enabled = _.filter(options, option => !this.disabled(option.name, query));
        const selected = _.first(enabled);
        if (selected) {
            return { name: selected.name, field: _.first(selected.fields) };
        } else {
            return null;
        }
    }

    /**
     * synchronous function to check the currently active visualisation option.
     */
    private activeOption(state: VisualizationSelection): VisualizationOption {
        return findByName(this.options, state.name);
    }

    /** check that the currently active visualisation is not disabled
     * in the current query state. If it is, resets the visualisation
     * to the default.
     */
    private checkActiveOption() {
        const active = this.activeOption(this.state$.value);
        if (this.disabled(active.name, this.query)) {
            this.setParams(this.getDefaultOption(this.options, this.query));
        }
    }
}
