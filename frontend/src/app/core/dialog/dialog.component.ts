import { Component, OnDestroy, OnInit, TemplateRef, DestroyRef, viewChild, inject } from '@angular/core';
import { NgbModal, NgbModalRef } from '@ng-bootstrap/ng-bootstrap';
import { SafeHtml } from '@angular/platform-browser';

import { navIcons } from '@shared/icons';
import { DialogService } from '@services';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

interface FooterDetails {
    label: string;
    link: string[];
}

@Component({
    selector: 'ia-dialog',
    templateUrl: './dialog.component.html',
    styleUrls: ['./dialog.component.scss'],
    standalone: false
})
export class DialogComponent implements OnDestroy, OnInit {
    modalTemplate = viewChild.required<TemplateRef<unknown>>('modalTemplate');

    public title: string;
    public innerHtml: SafeHtml;
    public footerDetails: FooterDetails;
    public isLoading = false;

    navIcons = navIcons;

    private modal: NgbModalRef;
    private dialogService = inject(DialogService);
    private modalService = inject(NgbModal);
    private destroyRef = inject(DestroyRef);

    ngOnInit(): void {
        this.dialogService.pageEvent
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe(event => {
                switch (event.status) {
                    case 'hide':
                        this.innerHtml = undefined;
                        this.isLoading = false;
                        this.close();
                        break;

                    case 'loading':
                        this.innerHtml = undefined;
                        this.isLoading = true;
                        this.open();
                        break;

                    case 'show':
                        this.innerHtml = event.html;
                        this.title = event.title;
                        this.isLoading = false;
                        this.footerDetails = event.footer ? {
                            label: event.footer.buttonLabel,
                            link: event.footer.routerLink
                        } : undefined;
                        this.open();
                        break;
                }
            });

        this.dialogService.closePage();
    }

    ngOnDestroy(): void {
        this.close();
    }

    public close(): void {
        this.modal?.close();
        this.modal = undefined;
    }

    private open(): void {
        const template = this.modalTemplate();
        if (!this.modal && template) {
            this.modal = this.modalService.open(template, {
                ariaLabelledBy: 'dialog-title',
                size: 'lg',
                scrollable: true,
            });
            this.modal.result.finally(() => {
                this.modal = undefined;
            });
        }
    }
}
