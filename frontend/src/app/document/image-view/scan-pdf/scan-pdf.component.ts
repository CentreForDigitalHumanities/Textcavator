import { Component, Input, HostListener, OnChanges, SimpleChanges } from '@angular/core';

import { ApiService } from '@services';


@Component({
    selector: 'ia-scan-pdf',
    templateUrl: './scan-pdf.component.html',
    styleUrls: ['./scan-pdf.component.scss'],
    standalone: false
})
export class ScanPdfComponent implements OnChanges {
    @Input() public imagePaths: string[];
    @Input() public zoomFactor: number;
    @Input() public showPage: number;

    public pdfSrc: ArrayBuffer;

    public pdfFile: any;

    public pdfNotFound = false;

    public path: URL;
    public page: number;

    public isLoaded = false;

    constructor(private apiService: ApiService) {
    }

    ngOnChanges(changes: SimpleChanges) {
        this.page = this.showPage + 1;
        if (changes.imagePaths) {
            this.path = new URL(this.imagePaths[0], window.location.href);
            this.apiService
                .getMedia({ args: this.path.search })
                .then((response) => {
                    this.pdfNotFound = false;
                    this.formatPdfResponse(response);
                    this.afterLoadComplete();
                })
                .catch(() => (this.pdfNotFound = true));
        }
    }

    formatPdfResponse(pdfData) {
        this.pdfSrc = pdfData.body;
    }

    /**
     * callback for ng2-pdf-viewer loadcomplete event,
     * fires after all pdf data is received and loaded by the viewer.
     */
    afterLoadComplete() {
        this.isLoaded = true;
    }

    onError(error: any) {
        console.log(error);
    }

    // code to implement scrolling with the mouse wheel
    // this is not currently feasible (container blocks scrolling interaction)
    // leaving in in case we want to implement this later
    // @HostListener('mousewheel', ['$event']) onMousewheel(event) {
    //     if(event.wheelDelta>0){
    //        this.zoomIn();
    //     }
    //     if(event.wheelDelta<0){
    //         this.zoomOut();
    //     }
    // }

}
