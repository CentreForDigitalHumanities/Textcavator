import { Component, Input, OnChanges, SimpleChanges, inject } from '@angular/core';
import { DownloadService, NotificationService } from '@app/services';
import {
    Download,
    DownloadOptions,
    TermFrequencyDownloadParameters,
    DownloadEncoding,
    DownloadTableFormat,
} from '@models';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { from, Observable, Subject } from 'rxjs';


@Component({
    selector: 'ia-download-options',
    templateUrl: './download-options.component.html',
    styleUrls: ['./download-options.component.scss'],
    standalone: false
})
export class DownloadOptionsComponent implements OnChanges {
    @Input() download: Download;

    isDownloading: boolean;
    confirm$ = new Subject<DownloadOptions>();

    activeModal = inject(NgbActiveModal);
    downloadService = inject(DownloadService);
    notificationService = inject(NotificationService);

    encodingOptions: DownloadEncoding[] = ['utf-8', 'utf-16'];
    encoding: DownloadEncoding = 'utf-8';

    formatOptions: DownloadTableFormat[] = ['long', 'wide'];
    format: DownloadTableFormat;


    /** whether the current download is a term frequency download */
    get isTermFrequency(): boolean {
        const termFrequencyTypes = [
            'aggregate_term_frequency',
            'date_term_frequency',
        ];
        return termFrequencyTypes.includes(this.download?.download_type);
    }

    /** whether to display long/wide format choice */
    get showFormatChoice(): boolean {
        if (this.isTermFrequency) {
            const parameters =
                ((this.download as Download)
                    .parameters as TermFrequencyDownloadParameters) || [];
            return parameters.length > 1;
        }
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (this.isTermFrequency) {
            this.format = 'long';
        }
    }

    confirmDownload() {
        this.isDownloading = true;
        const options: DownloadOptions = {
            encoding: this.encoding,
            table_format: this.format,
        };
        this.download$(this.download, options).subscribe({
            next: (res) => this.downloadResult(res, this.download.filename),
            error: (err) => this.downloadFailed(err),
        })
    }

    private download$(download: Download, options: DownloadOptions): Observable<any> {
        return from(this.downloadService.retrieveFinishedDownload(download.id, options));
    };

    private downloadResult(result, filename) {
        if (result.status == 200) {
            saveAs(result.body, filename);
            this.activeModal.close();
        } else {
            this.downloadFailed(result);
        }
    }

    private downloadFailed(result) {
        console.error(result);
        this.notificationService.showMessage('could not download file', 'danger');
        this.activeModal.close();
    }
}
