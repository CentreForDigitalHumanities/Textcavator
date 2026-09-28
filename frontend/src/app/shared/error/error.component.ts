import { Component, ElementRef, inject, input, OnDestroy, OnInit, viewChild } from '@angular/core';
import { NgbModal, NgbModalRef } from '@ng-bootstrap/ng-bootstrap';

export interface ErrorDetails {
    date: string;
    href: string;
    message: string;
};

@Component({
    selector: 'ia-error',
    templateUrl: './error.component.html',
    styleUrls: ['./error.component.scss'],
    standalone: false
})
export class ErrorComponent implements OnInit, OnDestroy {
    public readonly errorDetails = input.required<ErrorDetails>();
    private readonly errorModal = viewChild.required<ElementRef>('errorModal');

    private modal: NgbModalRef;
    private modalService = inject(NgbModal);

    public ngOnInit(): void {
        this.modal = this.modalService.open(this.errorModal(), {
            ariaLabelledBy: 'error-modal-title',
            role: 'alertdialog',
            centered: true,
            size: 'lg',
        });
    }

    public close(): void {
        this.modal?.close();
    }

    public ngOnDestroy(): void {
        this.close();
    }
}


