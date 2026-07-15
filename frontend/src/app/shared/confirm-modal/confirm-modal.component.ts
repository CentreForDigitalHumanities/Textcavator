import { Component, ElementRef, inject, Input, OnDestroy, Output, TemplateRef, ViewChild } from '@angular/core';
import { NgbModal, NgbModalRef } from '@ng-bootstrap/ng-bootstrap';
import { showLoading } from '@utils/utils';
import { BehaviorSubject, lastValueFrom, of, Subject, timer } from 'rxjs';


/**
 * Component to create a confirmation modal
 *
 * Input parameters:
 * - `actionText` (required): short label for the action; used as the header and the
 *   text for the confirm button.
 * - `icon`: icon to show in the confirm button
 * - `actionButtonClass`: additional CSS class to add to the confirm button, e.g.
 *   `is-danger` for destructive actions. Default is `is-primary`.
 * - `handleAsync`: can be used to delay closing the modal after confirming while the
 *   action is being processed. This is a function that takes the action parameters
 *   as input, and returns an observable. The modal will show a loading spinner while
 *   this is running.
 *
 * Output:
 * - `result`: If you did not include a `handleAsync` function, this emits when the user
 *   confirms the action, with the action parameters as payload. If you included a
 *   `handleAsync` function, this emits when the action is handled, with the output as
 *   payload.
 *
 * Use projected content to provide the text of the modal.
 *
 * Call `open()` to open the modal. Accepts an optional argument, which can contain any
 * data that is relevant in context. You can use `data` to access arguments. You can call
 * this with a `ViewChild`, but typically the easiest way is with a template variable
 * (see example below).
 *
 * Example usage:
 *
 * ```
 * <button (click)="confirm.open('something')">Do a thing</button>
 *
 * <ia-confirm-modal #confirm actionText="Do the thing">
 *    <p>
 *         Are you sure you want to do {{confirm.data}}?
 *    </p>
 * </ia-confirm-modal>
 * ```
 *
 * Note that projected content is still rendered if
 * the modal is inactive. (In which case `data` is undefined.)
 */
@Component({
    selector: 'ia-confirm-modal',
    standalone: false,
    templateUrl: './confirm-modal.component.html',
    styleUrl: './confirm-modal.component.scss'
})
export class ConfirmModalComponent implements OnDestroy {
    @Input({required: true}) actionText: string;
    @Input() icon: any;
    @Input() actionButtonClass: string = 'primary';
    @Input() disableCloseButton: boolean = false;
    @Output() accept = new Subject<any>();
    @Output() reject = new Subject<void>();

    @ViewChild('content') content: TemplateRef<HTMLElement>;

    confirmAction$ = new BehaviorSubject<{data: any} | undefined>(undefined);
    loading$ = new BehaviorSubject<boolean>(false);

    data: any; // for briefer notation, this provides the action data

    private modalService = inject(NgbModal);
    private modal: NgbModalRef;

    constructor() {
        this.confirmAction$.subscribe(data => this.data = data);
    }

    @Input() handleAsync = (data: any) => of(data);

    ngOnDestroy(): void {
        this.confirmAction$.complete();
        this.loading$.complete();
        this.accept.complete();
    }

    open(data?: any) {
        this.confirmAction$.next({data});
        this.modal = this.modalService.open(
            this.content, { ariaLabelledBy: 'modal-title' }
        );
    }

    confirm(data: any) {
        console.log(data);
        showLoading(
            this.loading$,
            lastValueFrom(this.handleAsync(data)),
        ).then(res => {
            this.confirmAction$.next(undefined);
            this.modal.close();
            this.accept.next(res)
        });
    }

    cancel() {
        this.confirmAction$.next(undefined);
        this.modal.dismiss();
        this.reject.next();
    }
}
