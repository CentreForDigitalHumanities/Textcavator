import * as _ from 'lodash';
import { Observable, Subject, from, of } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { mockUserResponse } from './user';
import { CorpusDocumentationPage, TaskResult, TasksOutcome } from '../app/models';
import { LimitedResultsDownloadParameters, NgramResults } from '../app/models/search-results';
import { corpusDefinitionFactory } from './corpus-definition';
import { APIEditableCorpus, CorpusDataFile } from '../app/models/corpus-definition';

export const fakeNgramResult: NgramResults = {
    words: [
        {
            label: 'the test',
            data: [1, 2]
        }
    ],
    totals: [
        { x: 3, y: 0, ngram: 'the test'},
    ],
    time_points: ['1900-1910', '1910-1920']
};

export class ApiServiceMock {
    public SessionExpiredSubject = new Subject();
    public SessionExpired = this.SessionExpiredSubject.asObservable();
    public stopPolling$: Subject<boolean> = new Subject<boolean>();

    constructor(public fakeResult: { [path: string]: any } = {}) {}

    public abortTasks(data: TaskResult) {
        return { success: true };
    }

    public get(path: string): Promise<any> {
        return Promise.resolve(this.fakeResult[path]);
    }

    public corpus() {
        // return this.get('corpus');
        return of(this.get('corpus'));
    }

    download(data: LimitedResultsDownloadParameters): Promise<any> {
        return Promise.resolve({});
    }

    public searchHistory() {
        return Promise.resolve([]);
    }

    public getWordcloudData() {
        return this.get('get_wordcloud_data');
    }

    public pollTasks(ids: string[], stopPolling$: Subject<void>): Observable<TasksOutcome> {
        const fakeResults = {
            // eslint-disable-next-line @typescript-eslint/naming-convention
            'ngram-task-id': fakeNgramResult,
        };
        const response: TasksOutcome = {
            status: 'done',
            results: ids.map((id) => fakeResults[id])
        };
        return from([response, response]).pipe(takeUntil(stopPolling$));
    }

    public downloads() {
        return Promise.resolve([]);
    }

    public getUser() {
        return of(mockUserResponse);
    }

    public keyInfo() {
        return of({ username: 'Thomas', email: 'thomas@cromwell.com' });
    }

    public corpusDocumentationPages(corpusName: string): Observable<CorpusDocumentationPage[]> {
        return of([{
            id: 1,
            corpus: corpusName,
            type: 'General',
            content: 'Example of _documentation_.',
            content_template: 'Example of _documentation_.',
            index: 1,
        }]);
    }

    public fieldCoverage() {
        return Promise.resolve({});
    }

    saveQuery() {
        return Promise.resolve();
    }

    requestMeQdia() {
        return Promise.resolve({});
    }

    userTags() {
        return of([]);
    }

    deleteTag() {
        return of();
    }

    corpusDefinitions(): Observable<APIEditableCorpus[]> {
        const data = [{ id: 1, active: false, definition: corpusDefinitionFactory() }];
        return of(data);
    }

    corpusDefinition(id: number): Observable<APIEditableCorpus> {
        const data = { id, active: false, definition: corpusDefinitionFactory() };
        return of(data);
    }

    createCorpus(data: APIEditableCorpus): Observable<APIEditableCorpus> {
        const result = _.merge({ id: 1 }, data);
        return of(result);
    }

    updateCorpus(_id: number, data: APIEditableCorpus): Observable<APIEditableCorpus> {
        return of(data);
    }

    listDataFiles(): Observable<CorpusDataFile[]> {
        return of([]);
    }

    corpusSchema(): Observable<any> {
        return of({});
    }
}
