import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import * as _ from 'lodash';

import { environment } from '@environments/environment';
import {
    AuthService,
    DownloadService,
    NotificationService,
    SearchService,
} from '@services/index';
import {
    Corpus,
    CorpusField,
    ExtraDownloadColumns,
    PendingDownload,
    QueryModel,
    SortState,
} from '@models/index';
import { actionIcons } from '@shared/icons';
import { TotalResults } from '@models/total-results';
import { SimpleStore } from '../store/simple-store';
import { Observable, map } from 'rxjs';
import { Router } from '@angular/router';
import { pageResultsParametersToParams } from '@utils/params';
import {
    DEFAULT_HIGHLIGHT_SIZE,
    PageResults,
    PageResultsParameters,
} from '@models/page-results';

type Encoding = 'utf-8' | 'utf-16';

@Component({
    selector: 'ia-download',
    templateUrl: './download.component.html',
    styleUrls: ['./download.component.scss'],
    standalone: false
})
export class DownloadComponent implements OnChanges {
    @Input() public corpus: Corpus;
    @Input() public queryModel: QueryModel;

    fieldOptions: { label: string, value: string }[];
    fieldSelection: string[];

    public isDownloading: boolean;
    public isModalActive = false;
    public isModalActiveError = false;

    public pendingDownload: PendingDownload;

    resultsConfig: PageResults;

    actionIcons = actionIcons;

    downloadLimit: number;

    canDownloadDirectly$: Observable<boolean>;

    encodingOptions: Encoding[] = ['utf-8', 'utf-16'];
    encoding: Encoding = 'utf-8';

    totalResults: TotalResults;
    downloadDisabled$: Observable<boolean>;

    tagsSelected = false;
    documentLinkSelected = false;

    private directDownloadLimit: number = environment.directDownloadLimit;
    private userDownloadLimit: number;

    private downloadsPageLink = {
        text: 'view downloads',
        route: ['/download-history'],
    };

    constructor(
        private downloadService: DownloadService,
        private notificationService: NotificationService,
        private searchService: SearchService,
        private authService: AuthService,
        private router: Router,
    ) {
        this.userDownloadLimit = this.authService.getCurrentUser()?.downloadLimit;
        this.downloadLimit = this.userDownloadLimit || this.directDownloadLimit;
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.corpus) {
            this.fieldOptions = this.corpus?.fields
                .filter(f => f.downloadable && !f.hidden)
                .map(f => ({value: f.name, label: f.displayName}));
            this.fieldSelection = _.filter(this.corpus?.fields, 'csvCore').map(f => f.name);
        }
        if (changes.queryModel) {
            this.totalResults?.complete();
            this.resultsConfig?.complete();
            this.totalResults = new TotalResults(
                new SimpleStore(), this.searchService, this.queryModel
            );
            this.downloadDisabled$ = this.totalResults.result$.pipe(
                map(result => result > 0)
            );
            this.canDownloadDirectly$ = this.totalResults.result$.pipe(
                map(this.enableDirectDownload.bind(this))
            );
            this.resultsConfig = new PageResults(
                new SimpleStore(), this.searchService, this.queryModel
            );
        }
    }

    onHighlightChange(event): void {
        if (event.target.checked) {
            this.resultsConfig.setParams({ highlight: DEFAULT_HIGHLIGHT_SIZE });
        } else {
            this.resultsConfig.setParams({ highlight: null });
        }
    }

    /** download short file directly */
    public confirmDirectDownload(): void {
        const sort = this.resultsConfig.state$.value.sort;
        const highlight = this.resultsConfig.state$.value.highlight;
        this.isDownloading = true;
        this.downloadService
            .download(
                this.corpus,
                this.queryModel,
                this.getColumnNames(),
                this.directDownloadLimit,
                this.resultsRoute(this.queryModel, sort, highlight),
                sort,
                highlight,
                { encoding: this.encoding },
                this.extraColumns(),
            )
            .catch((error) => {
                this.notificationService.showMessage(error);
            })
            .then(() => {
                this.isDownloading = false;
                this.pendingDownload = undefined;
            });
    }


    /** start backend task to create csv file */
    longDownload(): void {
        const sort = this.resultsConfig.state$.value.sort;
        const highlight = this.resultsConfig.state$.value.highlight;
        this.downloadService
            .downloadTask(
                this.corpus,
                this.queryModel,
                this.getColumnNames(),
                this.resultsRoute(this.queryModel, sort, highlight),
                sort,
                highlight,
                this.extraColumns(),
            )
            .then((results) => {
                this.notificationService.showMessage(
                    'Downloading CSV file... A link will be sent to your email address shortly.',
                    'success',
                    this.downloadsPageLink
                );
            })
            .catch((error) => {
                this.notificationService.showMessage(error, 'danger');
            });
    }

    private enableDirectDownload(totalResults: number): boolean {
        const totalToDownload = _.min([totalResults, this.downloadLimit]);
        return totalToDownload <= this.directDownloadLimit;
    }

    private getColumnNames(): string[] {
        let selected: string[];
        if (this.fieldSelection === undefined) {
            selected = this.corpus.fields.filter((field) => field.csvCore).map(f => f.name);
        } else {
            selected = _.clone(this.fieldSelection);
        }
        return selected
    }

    private extraColumns(): ExtraDownloadColumns {
        const selected = [];
        if (this.resultsConfig.state$.value.highlight) {
            selected.push('context');
        }
        if (this.tagsSelected) {
            selected.push('tags');
        }
        if (this.documentLinkSelected) {
            selected.push('document_link');
        }
        return selected;
    }

    /**
     * Generate URL to view these results in the web interface
     */
    private resultsRoute(
        queryModel: QueryModel, sort: SortState, highlight?: number
    ): string {
        const resultsParameters: PageResultsParameters = {sort, from: 0, size: 20, highlight };
        const queryParams = {
            ...queryModel.toQueryParams(),
            ...pageResultsParametersToParams(resultsParameters, queryModel.corpus)
        };
        const tree = this.router.createUrlTree(
            ['/search', queryModel.corpus.name],
            { queryParams }
        );
        return tree.toString();
    }
}
