import {
    Component,
    Input,
    OnChanges,
    OnDestroy,
    SimpleChanges,
    TemplateRef,
    ViewChild,
} from '@angular/core';
import { NgbModal, NgbModalRef } from '@ng-bootstrap/ng-bootstrap';
import {
    DocumentFocus,
    DocumentPage,
    DocumentView,
} from '@models/document-page';
import { takeUntil } from 'rxjs/operators';
import _ from 'lodash';
import { FoundDocument, QueryModel } from '@models';
import { Subject } from 'rxjs';
import { actionIcons, documentIcons } from '@shared/icons';

@Component({
    selector: 'ia-document-popup',
    templateUrl: './document-popup.component.html',
    styleUrls: ['./document-popup.component.scss'],
    standalone: false
})
export class DocumentPopupComponent implements OnChanges, OnDestroy {
    @Input() page: DocumentPage;
    @Input() queryModel: QueryModel;
    @ViewChild('modalTemplate', { static: true }) modalTemplate: TemplateRef<HTMLElement>;

    document: FoundDocument;
    view: DocumentView;
    
    public documentPageLink: string[];

    actionIcons = actionIcons;
    documentIcons = documentIcons;

    showNamedEntities = false;
    showNEROption = false;

    private refresh$ = new Subject<void>();
    private modal: NgbModalRef;

    constructor(private modalService: NgbModal) { }

    get contextDisplayName(): string {
        if (this.document.corpus.documentContext) {
            return this.document.corpus.documentContext.displayName;
        }
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.queryModel) {
            this.showNEROption = this.queryModel.corpus.hasNamedEntities;
        }
        if (changes.page) {
            this.refresh$.next();
            this.focusUpdate();

            this.page.focus$.pipe(
                takeUntil(this.refresh$),
            ).subscribe(this.focusUpdate.bind(this));
        }
    }

    ngOnDestroy(): void {
        this.refresh$.next();
        this.refresh$.complete();
        this.close();
    }

    focusUpdate(focus?: DocumentFocus): void {
        if (focus) {
            this.document = focus.document;
            this.view = focus.view;
            this.documentPageLink = ['/document', this.document.corpus.name, this.document.id];
            this.open();
        } else {
            this.document = undefined;
            this.documentPageLink = undefined;
            this.close();
        }
    }

    close(): void {
        this.modal?.close();
        this.modal = undefined;
    }

    toggleNER(active: boolean): void {
        this.showNamedEntities = active;
    }

    documentPosition(document: FoundDocument, page: DocumentPage) {
        return page.from + document.position;
    }

    private open(): void {
        if (!this.document || this.modal) {
            return;
        }

        this.modal = this.modalService.open(this.modalTemplate, {
            ariaLabelledBy: 'dialog-title',
            backdrop: true,
            keyboard: true,
            scrollable: true,
            size: 'xl',
        });
        this.modal.result.finally(() => {
            this.modal = undefined;
        });
    }
}
