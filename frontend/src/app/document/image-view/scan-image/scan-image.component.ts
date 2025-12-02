import { AfterViewInit, Component, ElementRef, Input, OnChanges, ViewChild, SimpleChanges } from '@angular/core';

import { ImageViewer } from 'iv-viewer';

@Component({
    selector: 'ia-scan-image',
    templateUrl: './scan-image.component.html',
    styleUrls: ['./scan-image.component.scss'],
    standalone: false
})
export class ScanImageComponent implements AfterViewInit, OnChanges {
    @Input() public imagePaths: string[];
    @Input() public zoomFactor: number;
    @Input() public showPage: number;
    @ViewChild('imageContainer', {static: true}) public container: ElementRef;

    public viewer: any = null;


    ngAfterViewInit() {
        this.viewer = new ImageViewer(this.container.nativeElement);
        this.showCurrentImage();
    }

    ngOnChanges(changes: SimpleChanges) {
        if (this.viewer) {
            this.showCurrentImage();
            if (changes['zoomFactor']) {
                this.viewer.zoom(this.zoomFactor * 100);
            }
        }
    }

    showCurrentImage() {
        const imgObj = this.imagePaths[this.showPage];
        this.viewer.load(imgObj, imgObj);
    }
}
