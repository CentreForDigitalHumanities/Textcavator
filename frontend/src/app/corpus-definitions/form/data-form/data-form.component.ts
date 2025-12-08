import { Component, OnDestroy, OnInit} from '@angular/core';
import { CorpusDataFile, DataFileInfo } from '@models/corpus-definition';
import { ApiService, DialogService } from '@services';
import { actionIcons, formIcons } from '@shared/icons';
import { CorpusDefinitionService } from 'app/corpus-definitions/corpus-definition.service';
import * as _ from 'lodash';
import { MenuItem } from 'primeng/api';
import {
    BehaviorSubject,
    filter,
    forkJoin,
    map,
    Observable,
    shareReplay,
    Subject,
    switchMap,
    take,
    takeUntil,
    withLatestFrom,
} from 'rxjs';

type DataFileState =
    | 'noneUploaded'
    | 'firstUploaded'
    | 'firstConfirmed'
    | 'newUploaded';

@Component({
    selector: 'ia-data-form',
    templateUrl: './data-form.component.html',
    styleUrl: './data-form.component.scss',
    standalone: false,
})
export class DataFormComponent implements OnInit, OnDestroy {
    actionIcons = actionIcons;
    formIcons = formIcons;

    filesChanged$ = new Subject<void>();

    dataFiles$ = new BehaviorSubject<CorpusDataFile[] | undefined>(undefined);
    fileState$: Observable<DataFileState>;
    unconfirmed$: Observable<CorpusDataFile>;
    confirmed$: Observable<CorpusDataFile>;

    error$ = new BehaviorSubject<Error | undefined>(undefined);
    destroy$ = new Subject<void>();

    nextStep$: Observable<MenuItem> = this.corpusDefService.steps$.pipe(
        map((steps) => steps[1]),
    );

    constructor(
        private apiService: ApiService,
        private corpusDefService: CorpusDefinitionService,
        private dialogService: DialogService,
    ) {}

    ngOnInit() {
        this.confirmed$ = this.dataFiles$.pipe(
            filter(_.negate(_.isUndefined)),
            map((files) => files.find((file) => file.confirmed)),
            shareReplay(1),
        );

        this.unconfirmed$ = this.dataFiles$.pipe(
            filter(_.negate(_.isUndefined)),
            map((files) => files.find((file) => !file.confirmed)),
            shareReplay(1),
        );

        this.filesChanged$.pipe(takeUntil(this.destroy$)).subscribe({
            next: () => {
                this.refreshDataFiles();
            },
        });

        this.fileState$ = this.dataFiles$.pipe(
            map(this.datafilesToState),
            shareReplay(1),
        );

        this.refreshDataFiles();
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
        this.dataFiles$.complete();
    }

    confirmFile() {
        this.unconfirmed$
            .pipe(
                takeUntil(this.destroy$),
                switchMap((datafile) =>
                    this.apiService.patchDataFile(datafile.id, {
                        confirmed: true,
                    }),
                ),
            )
            .subscribe({
                next: (datafile) => {
                    this.setCorpusFields(datafile.csv_info);
                    this.filesChanged$.next();
                },
                error: (err) => this.error$.next(err),
            });
    }

    onReplaceAccept = () => {
        // Confirm file replacement
        // Removes the old file, then confirms the new
        const removeConfirmed = this.confirmed$.pipe(
            take(1),
            switchMap((df) => this.apiService.deleteDataFile(df)),
        );

        removeConfirmed
            .pipe(
                withLatestFrom(this.unconfirmed$),
                map(([_, file]) => file),
                switchMap((file) =>
                    this.apiService.patchDataFile(file.id, { confirmed: true }),
                ),
            )
            .subscribe({
                next: (datafile) => {
                    this.setCorpusFields(datafile.csv_info);
                    this.refreshDataFiles();
                },
                error: (error) => this.error$.next(error),
            });
    };

    onReplaceReject = () =>
        // Remove unconfirmed (new) file
        this.unconfirmed$
            .pipe(switchMap((file) => this.apiService.deleteDataFile(file)))
            .subscribe({
                next: () => this.refreshDataFiles(),
                error: (error) => this.error$.next(error),
            });

    handleReset = (files: CorpusDataFile[]): Observable<any> => {
        const requests = files.map((file) =>
            this.apiService.deleteDataFile(file),
        );
        return forkJoin(requests);
    };

    onResetComplete() {
        // reset corpus fields
        this.corpusDefService.setFields([]);
        this.filesChanged$.next();
    }

    onUpload(event: InputEvent) {
        const files: File[] = event.target['files'];
        const file = files ? _.first(files) : undefined;
        this.createDataFile(file);
    }

    openDocumentation() {
        this.dialogService.showManualPage('uploading-source-data');
    }

    private createDataFile(file: File): void {
        const corpusId = this.corpusDefService.corpus$.value.id;
        this.apiService
            .createDataFile(corpusId, file)
            .pipe(takeUntil(this.destroy$))
            .subscribe({
                next: () => this.filesChanged$.next(),
                error: (err) => this.error$.next(err),
            });
    }

    private refreshDataFiles(): void {
        this.apiService
            .listDataFiles(this.corpusDefService.corpus$.value.id, true)
            .pipe(filter(_.negate(_.isUndefined)), takeUntil(this.destroy$))
            .subscribe({
                next: (datafiles) => {
                    this.dataFiles$.next(datafiles);
                    this.corpusDefService.refreshCorpus();
                },
                error: (err) => this.error$.next(err),
            });
    }

    private setCorpusFields(info: DataFileInfo) {
        const fields = _.map(info.fields, (field) =>
            this.corpusDefService.makeDefaultField(field.type, field.name),
        );
        this.nextStep();
        this.corpusDefService.setFields(fields);
    }

    private nextStep() {
        this.corpusDefService.corpus$.value.definitionUpdated$
            .pipe(take(1), takeUntil(this.destroy$))
            .subscribe(() => this.corpusDefService.activateStep(2));
    }

    private datafilesToState = (files: CorpusDataFile[]): DataFileState => {
        if (_.isEmpty(files)) {
            return 'noneUploaded';
        }
        if (files.length == 1) {
            if (_.some(files, { confirmed: false })) {
                return 'firstUploaded';
            }
            if (_.some(files, { confirmed: true })) {
                return 'firstConfirmed';
            }
        }
        if (
            files?.length === 2 &&
            _.some(files, { confirmed: true }) &&
            _.some(files, { confirmed: false })
        ) {
            return 'newUploaded';
        }
    };
}
