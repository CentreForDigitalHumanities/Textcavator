import { Component, Input, OnChanges, OnDestroy, SimpleChanges } from '@angular/core';
import { CorpusDefinition } from '@models/corpus-definition';
import { APIIndexHealth, isComplete, JobStatus } from '@models/indexing';
import { ApiService, CorpusService } from '@services';
import { actionIcons } from '@shared/icons';
import * as _ from 'lodash';
import { map, Subject, switchMap, merge, filter } from 'rxjs';

/** Possible states for the interface of this component */
type DisplayState = {
    // connection issues in the backend (indexing disabled)
    status: 'no connection',
} | {
    // indexing available and required to use the corpus
    status: 'index required',
    // there can be several reasons for this; note that these are not mutually exclusive,
    // but reporting one the user is enough. Listed here in order of preference,
    // e.g. if the data is outdated and the job was cancelled, just say the data is outdated.
    reason: 'no index' | 'outdated data' | 'outdated configuration' | 'job cancelled',
} | {
    // index in progress
    status: 'working',
} | {
    // index complete (indexing disabled, corpus can be activated)
    status: 'index ready',
} | {
    // index job failed (should never happen, user must contact admin)
    status: 'indexing failed',
} | {
    // corpus not index-ready (e.g. missing data or fields)
    status: 'corpus invalid',
    reason: string,
};

/** Converts the API index health response to a display state for this component.
 *
 * Breaks down possible scenarios.
 */
const healthToDisplayState = (health: APIIndexHealth): DisplayState => {
    // all requirements for the "ready" state
    if (
        health.server_active &&
        health.index_active &&
        health.job_status == JobStatus.Done &&
        health.index_compatible &&
        health.includes_latest_data
    ) {
        return { status: 'index ready' };
    }
    // otherwise, go over alternatives
    if (!health.server_active) {
        return { status: 'no connection' };
    }
    if (health.job_status && !(isComplete(health.job_status))) {
        return { status: 'working' };
    }
    if (health.job_status == JobStatus.Error) {
        return { status: 'indexing failed' };
    }
    if (!health.corpus_ready_to_index) {
        return { status: 'corpus invalid', reason: health.corpus_validation_feedback };
    }
    if (!health.index_active) {
        return { status: 'index required', reason: 'no index' };
    }
    if (!health.index_compatible) {
        return { status: 'index required', reason: 'outdated configuration' };
    }
    if (!health.includes_latest_data) {
        return { status: 'index required', reason: 'outdated data' };
    }
    if (health.job_status == JobStatus.Aborted || health.job_status == JobStatus.Cancelled) {
        return { status: 'index required', reason: 'job cancelled' };
    }
};

@Component({
    selector: 'ia-index-form',
    templateUrl: './index-form.component.html',
    styleUrl: './index-form.component.scss',
    standalone: false,
})
export class IndexFormComponent implements OnChanges, OnDestroy {
    @Input({required: true}) corpus: CorpusDefinition;

    state$ = new Subject<DisplayState>;
    destroy$ = new Subject<void>();

    actionIcons = actionIcons;

    private jobID: number;
    private stopping$ = new Subject<boolean>();

    constructor(
        private apiService: ApiService,
    ) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.corpus) {
            this.apiService.getIndexHealth(this.corpus.id).subscribe(health => {
                const state = healthToDisplayState(health);
                this.state$.next(state);
                if (state.status == 'working') {
                    this.jobID = health.latest_job;
                    this.pollJob();
                }
            });
        }
    }

    ngOnDestroy(): void {
        this.stopping$.complete();
        this.destroy$.next();
        this.destroy$.complete();
    }

    startIndex() {
        this.state$.next({ status: 'working' });
        this.apiService.createIndexJob(this.corpus.id).subscribe((response) => {
            this.jobID = response.id;
            this.pollJob();
        });
    }

    stopIndex() {
        this.stopping$.next(true);
        this.apiService.stopIndexJob(this.jobID).subscribe({
            next: () => {
                this.stopping$.next(false);
                this.state$.next({ status: 'index required', reason: 'job cancelled' });
            },
            error: () => {
                this.stopping$.next(false);
                this.state$.next({ status: 'indexing failed' });
            },
        });
    }

    toggleCorpusActive() {
        this.corpus.active = !this.corpus.active;
        this.corpus.save();
    }

    stateClass(state: DisplayState) {
        switch (state.status) {
            case 'no connection':
            case 'indexing failed':
                return 'is-danger';
            case 'index ready':
                return 'is-success';
            case 'corpus invalid':
                return 'is-warning';
            default:
                '';
        }
    }

    private pollJob() {
        this.apiService.pollIndexJob(
            this.jobID,
            merge(this.destroy$, this.stopping$),
        ).pipe(
            switchMap(() => this.apiService.getIndexHealth(this.corpus.id)),
            map(healthToDisplayState),
        ).subscribe(state => this.state$.next(state));
    }
}
