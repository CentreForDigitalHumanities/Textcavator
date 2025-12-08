import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { FoundDocument, Corpus } from '@models';
import { ImageInfo } from '@models/image';
import { ApiService } from '@services';
import { scanIcons, actionIcons, formIcons } from '@shared/icons';

@Component({
    selector: 'ia-image-view',
    templateUrl: './image-view.component.html',
    styleUrls: ['./image-view.component.scss'],
    standalone: false
})
export class ImageViewComponent implements OnChanges {
    @Input() public corpus: Corpus;
    @Input() public document: FoundDocument;

    public imagePaths: string[];
    public mediaType: string;
    public allowDownload: boolean;

    scanIcons = scanIcons;
    actionIcons = actionIcons;
    formIcons = formIcons;

    public noImages: boolean;

    public pageIndices: number[];
    public showPage: number;
    public initialPage = 1;

    public downloadPath: string; // optional: downloadable content may differ from displayed content
    public zoomFactor = 1.0;

    private imageInfo: ImageInfo;
    private maxZoomFactor = 1.7;

    constructor(
        private apiService: ApiService,
    ) {}

    ngOnChanges(changes: SimpleChanges) {
        if (changes.corpus) {
            this.allowDownload = this.corpus.allowImageDownload;
            this.mediaType = this.corpus.scanImageType;
        }
        if (
            changes.document &&
            changes.document.previousValue !== changes.document.currentValue
        ) {
            this.imagePaths = undefined;
            this.apiService
                .requestMedia({
                    corpus: this.corpus.name,
                    document: this.document,
                })
                .then((response) => {
                    this.noImages = false;
                    this.imagePaths = response.media;
                    if (response.info) {
                        this.imageInfo = response.info;
                        this.showPage =
                            Number(this.imageInfo.homePageIndex) - 1;
                        this.pageIndices = this.imageInfo.pageNumbers.map((d) =>
                            Number(d)
                        );
                        this.initialPage = this.pageIndices[this.showPage]; //1-indexed
                    } else {
                        this.imageInfo = undefined;
                        const totalPages = this.imagePaths.length;
                        this.pageIndices = Array.from(
                            Array(totalPages + 1).keys()
                        ).slice(1);
                        this.showPage = this.pageIndices.indexOf(
                            this.initialPage
                        );
                    }
                })
                .catch((err) => (this.noImages = true));
        }
    }

    zoomIn() {
        if (this.zoomFactor <= this.maxZoomFactor) {
            this.zoomFactor += 0.1;
        }
    }

    zoomOut() {
        this.zoomFactor -= 0.1;
    }

    resetZoom() {
        this.zoomFactor = 1;
    }

    download() {
        const url = this.imagePaths[this.showPage];
        window.location.href = url;
    }

    pageIndexChange(event: number) {
        this.showPage = this.pageIndices.indexOf(event);
    }
}
