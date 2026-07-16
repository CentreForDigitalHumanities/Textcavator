import { Component, OnInit } from '@angular/core';
import * as _ from 'lodash';
import {
    Download,
    DownloadOptions,
    DownloadParameters,
    DownloadType,
    QueryModel,
} from '@models';
import {
    ApiService,
    CorpusService,
    DownloadService,
    NotificationService,
} from '@services';
import { HistoryDirective } from '../history.directive';
import { findByName } from '@utils/utils';
import { actionIcons } from '@shared/icons';
import {
    downloadQueryModel,
    downloadQueryModels,
} from '@utils/download-history';
import { Title } from '@angular/platform-browser';
import { pageTitle } from '@utils/app';

@Component({
    selector: 'ia-download-history',
    templateUrl: './download-history.component.html',
    styleUrls: ['./download-history.component.scss'],
    standalone: false
})
export class DownloadHistoryComponent extends HistoryDirective implements OnInit {
    downloads: Download[];

    actionIcons = actionIcons;

    itemToDownload: Download;

    constructor(
        private downloadService: DownloadService,
        private apiService: ApiService,
        corpusService: CorpusService,
        private notificationService: NotificationService,
        private title: Title,
    ) {
        super(corpusService);
    }

    ngOnInit(): void {
        this.title.setTitle(pageTitle('Downloads'));
        this.retrieveCorpora();
        this.apiService.downloads()
            .then(downloadHistory => this.downloads = this.sortByDate(downloadHistory))
            .catch(err => console.error(err));
    }

    downloadType(type: DownloadType): string {
        const displayNames = {
            search_results: 'Search results',
            date_term_frequency: 'Term frequency',
            aggregate_term_frequency: 'Term frequency',
            ngram: 'Neighbouring words'
            // timeline/histogram distinction is relevant for backend but not for the user
        };
        return displayNames[type];
    }

    queryText(download: Download): string {
        const queryModels = this.getAllQueryModels(download);
        if (queryModels) {
            const queryTexts = queryModels.map(model => model.queryText);
            return _.join(queryTexts, ', ');
        } else {
            return '';
        }
    }

    getAllQueryModels(download: Download): QueryModel[] {
        const corpus = findByName(this.corpora, download.corpus);
        if (corpus) {
            return downloadQueryModels(download, corpus);
        }
    }

    getQueryModel(download: Download): QueryModel {
        const corpus = findByName(this.corpora, download.corpus);
        if (corpus) {
            return downloadQueryModel(download, corpus);
        }
    }

    getFields(download: Download): string {
        const parameters: DownloadParameters = download.parameters;
        const fieldNames =  'fields' in parameters ?
            parameters.fields : [parameters[0].field_name];
        const corpus = findByName(this.corpora, download.corpus);
        if (corpus) {
            const fields = fieldNames.map(fieldName =>
                findByName(corpus.fields, fieldName)?.displayName
            ).filter(_.negate(_.isUndefined));
            return _.join(fields, ', ');
        }
    }

    downloadFile(download: Download, options: DownloadOptions) {
        this.downloadService.retrieveFinishedDownload(download.id, options).then( result => {
            if (result.status === 200) {
                saveAs(result.body, download.filename);
                this.itemToDownload = undefined;
            } else {
                this.downloadFailed(result);
            }
        }).catch(this.downloadFailed.bind(this));
    }

    downloadFailed(result) {
        console.error(result);
        this.notificationService.showMessage('could not download file', 'danger');
        this.itemToDownload = undefined;
    }
}
