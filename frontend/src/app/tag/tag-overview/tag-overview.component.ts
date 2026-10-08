import { Component, inject, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { isUndefined } from 'lodash';
import { Corpus, QueryModel, Tag } from '@models';
import { isTagFilter } from '@models/tag-filter';
import { CorpusService } from '@services';
import { TagService } from '@services/tag.service';
import { actionIcons, formIcons } from '@shared/icons';
import { findByName } from '@utils/utils';
import { Title } from '@angular/platform-browser';
import { pageTitle } from '@utils/app';
import { NgbModal, NgbModalRef } from '@ng-bootstrap/ng-bootstrap';
import { FormControl, FormGroup, Validators } from '@angular/forms';

@Component({
    selector: 'ia-tag-overview',
    templateUrl: './tag-overview.component.html',
    styleUrls: ['./tag-overview.component.scss'],
    standalone: false
})
export class TagOverviewComponent implements OnInit {
    @ViewChild('editFormModal') editFormTemplate: TemplateRef<HTMLElement>;

    tags$ = this.tagService.tags$;

    actionIcons = actionIcons;
    formIcons = formIcons;

    corpora: Corpus[];

    modalType: 'edit' | 'create';

    editForm = new FormGroup({
        name: new FormControl<string>('', {
            nonNullable: true,
            validators: [Validators.required],
        }),
        description: new FormControl<string>(''),
    });

    handleDelete = this.tagService.deleteTag.bind(this.tagService);

    private modalService = inject(NgbModal);
    private modal: NgbModalRef;

    constructor(
        private tagService: TagService,
        private corpusService: CorpusService,
        private title: Title,
    ) {}

    async ngOnInit(): Promise<void> {
        this.corpora = await this.corpusService.get(false);
        this.tagService.fetch();
        this.title.setTitle(pageTitle('Tags'));
    }

    startEdit(tag: Tag) {
        this.editForm.setValue({name: tag.name, description: tag.description});
        this.modalType = 'edit';
        this.modal = this.modalService.open(this.editFormTemplate);
    }

    startCreate() {
        this.editForm.reset();
        this.modalType = 'create';
        this.modal = this.modalService.open(this.editFormTemplate);
    }

    cancelEdit() {
        this.modal?.close();
        this.editForm.reset();
        this.modalType = undefined;
    }

    finishEdit() {
        this.tagService
            .updateTag(this.editForm.getRawValue() as Tag)
            .subscribe(() => this.cancelEdit());
    }

    finishCreate() {
        this.tagService
            .makeTag(
                this.editForm.controls.name.value,
                this.editForm.controls.description.value,
            ).subscribe(() => this.cancelEdit());
    }

    makeQueryParams(corpusName, tag) {
        if (this.corpora) {
            const corpus = findByName(this.corpora, corpusName);

            if (corpus) {
                const query = new QueryModel(corpus);
                const tagfilter = query.filters.find(isTagFilter);
                tagfilter.set([tag.id]);

                const params = query.toQueryParams();
                return params;
            }
        }
    }
}
