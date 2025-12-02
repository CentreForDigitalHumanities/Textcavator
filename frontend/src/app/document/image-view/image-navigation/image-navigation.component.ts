import { Component, EventEmitter, Input, OnInit, Output, OnChanges } from '@angular/core';
import { scanIcons } from '@shared/icons';

@Component({
    selector: 'ia-image-navigation',
    templateUrl: './image-navigation.component.html',
    styleUrls: ['./image-navigation.component.scss'],
    standalone: false
})
export class ImageNavigationComponent implements OnChanges {
    @Input() public pageIndices: number[];
    @Input() public initialPage: number;

    @Output()
    public pageIndexChange = new EventEmitter<number>();

    public page: number;
    public firstPage: number;
    public lastPage: number;

    scanIcons = scanIcons;

    // array used for generating navigation buttons
    public buttonArray: number[];
    // the maximum number of buttons to display for navigation
    private maxButtons = 8;

    constructor() { }

    ngOnChanges() {
        this.page = this.initialPage;
        this.firstPage = this.pageIndices[0];
        this.lastPage = this.pageIndices[this.pageIndices.length - 1];
        this.calculateButtonArray();
    }

    prevPage() {
        this.page =
            this.page - 1 > this.firstPage - 1 ? this.page - 1 : this.lastPage;
        this.calculateButtonArray();
        this.pageIndexChange.emit(this.page);
    }

    nextPage() {
        this.page =
            this.page + 1 < this.lastPage + 1 ? this.page + 1 : this.firstPage;
        this.calculateButtonArray();
        this.pageIndexChange.emit(this.page);
    }

    goToPage(event: number) {
        this.page = event;
        this.calculateButtonArray();
        this.pageIndexChange.emit(this.page);
    }

    /**
     * calculate the array of page numbers used for the navigation buttons
     */
    calculateButtonArray() {
        if (this.pageIndices.length < this.maxButtons) {
            this.buttonArray = this.pageIndices;
        } else {
            const curPageIndex = this.pageIndices.indexOf(this.page);
            switch (curPageIndex) {
                case 0:
                    this.buttonArray = this.pageIndices.slice(
                        curPageIndex,
                        curPageIndex + this.maxButtons
                    );
                    break;
                case this.pageIndices.length:
                    this.buttonArray = this.pageIndices.slice(
                        curPageIndex - this.maxButtons,
                        curPageIndex
                    );
                    break;
                default:
                    this.buttonArray = this.pageIndices.slice(
                        curPageIndex - this.maxButtons / 2,
                        curPageIndex + this.maxButtons / 2
                    );
                    break;
            }
        }
    }
}
