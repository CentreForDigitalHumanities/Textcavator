import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed, fakeAsync, tick } from '@angular/core/testing';

import { ApiService } from './api.service';
import { HttpClient, HttpErrorResponse, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { fakeNgramResult } from '@mock-data/api';
import { Subject, from, throwError } from 'rxjs';
import { TaskResult, TasksOutcome } from '@models';

describe('ApiService', () => {
    let service: ApiService;
    let httpClient: HttpClient;
    let httpMock: HttpTestingController;
    const pollingCallback = {
        next: (result) => result,
        error: (error) => error,
        complete: () => {}
    };

    beforeEach(() => {
        TestBed.configureTestingModule({
    imports: [],
    providers: [provideHttpClient(withInterceptorsFromDi()), provideHttpClientTesting()]
});
        service = TestBed.inject(ApiService);
        httpClient = TestBed.inject(HttpClient);
        httpMock = TestBed.inject(HttpTestingController);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    it('should poll tasks and only pass on successful ones', fakeAsync(() => {
        const stopPolling$ = new Subject<void>();
        const testData: TasksOutcome[] = [
            { status: 'working' },
            { status: 'done', results: [fakeNgramResult] }
        ];
        service.getTasksStatus = (tasks: TaskResult) => from(testData);
        spyOn(pollingCallback, 'next');
        service.pollTasks(['fake_ids'], stopPolling$).subscribe(pollingCallback);
        tick(5000);
        expect(pollingCallback.next).toHaveBeenCalled();
        stopPolling$.next();
    }));

    it('should poll tasks and throw an error on failure', fakeAsync(() => {
        const stopPolling$ = new Subject<void>();
        spyOn(pollingCallback, 'error');
        const errorResponse = new HttpErrorResponse(
            {error: {detail: 'Task failed'}, status: 500}
        );
        service.getTasksStatus = (tasks: TaskResult) => throwError(errorResponse);
        service.pollTasks(['fake_ids'], stopPolling$).subscribe(pollingCallback);
        tick(5000);
        expect(pollingCallback.error).toHaveBeenCalled();
        stopPolling$.next();
    }));

    it('should poll tasks and complete if stopPolling$ is triggered', fakeAsync(() => {
        const stopPolling$ = new Subject<void>();
        spyOn(pollingCallback, 'complete');
        const testData: TasksOutcome[] = [
            { status: 'working' },
            { status: 'done', results: [fakeNgramResult] }
        ];
        service.getTasksStatus = (tasks: TaskResult) => from(testData);
        service.pollTasks(['fake_ids'], stopPolling$).subscribe(pollingCallback);
        tick(100);
        stopPolling$.next();
        expect(pollingCallback.complete).toHaveBeenCalled();
    }));

});
