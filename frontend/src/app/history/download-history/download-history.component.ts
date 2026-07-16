import { Component, inject, OnInit } from '@angular/core';
import * as _ from 'lodash';
import {
    Download,
    DownloadParameters,
    DownloadType,
    QueryModel,
} from '@models';
import {
    ApiService,
    CorpusService,
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
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { DownloadOptionsComponent } from '@app/download/download-options/download-options.component';

@Component({
    selector: 'ia-download-history',
    templateUrl: './download-history.component.html',
    styleUrls: ['./download-history.component.scss'],
    standalone: false
})
export class DownloadHistoryComponent extends HistoryDirective implements OnInit {
    downloads: Download[];

    actionIcons = actionIcons;

    private modalService = inject(NgbModal);

    constructor(
        private apiService: ApiService,
        corpusService: CorpusService,
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

    showOptions(download: Download) {
        const modalRef = this.modalService.open(DownloadOptionsComponent);
        const component = modalRef.componentInstance as DownloadOptionsComponent;
        component.download = download;
    }
}
