/* eslint-disable @typescript-eslint/member-ordering */
import * as _ from 'lodash';
import { Component, DestroyRef, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CorpusField, QueryModel } from '@models/index';
import { actionIcons } from '@shared/icons';
import { searchFieldOptions } from '@utils/search-fields';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
    selector: 'ia-select-field',
    templateUrl: './select-field.component.html',
    styleUrls: ['./select-field.component.scss'],
    standalone: false
})
export class SelectFieldComponent implements OnChanges {
    @Input({ required: true }) queryModel!: QueryModel;

    /** searchable fields
     *
     * This includes multifield "variants", i.e. "*.text" and "*.stemmed" fields
     */
    private availableFields: CorpusField[];
    /** the options displayed in the dropdown element
     *
     * Must be a plain JS object, not a CorpusField instance; see
     * https://github.com/orgs/primefaces/discussions/3695#discussioncomment-12582579
     */
    public options: { label: string, value: string }[];
    /** user selection (field names) */
    selected: string[];
    /** whether to display all field options, or just the core ones */
    public allVisible = false;

    actionIcons = actionIcons;

    constructor(private destroyRef: DestroyRef) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.queryModel) {
            this.availableFields = searchFieldOptions(this.queryModel.corpus);
            this.setOptions();
            this.setStateFromQueryModel();
            this.queryModel.update.pipe(
                takeUntilDestroyed(this.destroyRef),
            ).subscribe(() => this.setStateFromQueryModel());
        }
    }

    setStateFromQueryModel() {
        if (this.queryModel.searchFields) {
            this.selected = this.queryModel.searchFields.map(f => f.name);
        } else {
            this.selected = [];
        }
    }

    public toggleAllFields() {
        this.allVisible = !this.allVisible;
        this.setOptions();
    }

    public onUpdate() {
        const fields = this.availableFields.filter(f => this.selected.includes(f.name));
        this.queryModel.setParams({ searchFields: fields });
    }

    setOptions() {
        let fields: CorpusField[];
        if (this.allVisible) {
            fields = this.availableFields.sort(f => f.searchFieldCore ? 0 : 1);
        } else {
            fields = this.availableFields.filter(f => f.searchFieldCore);
        }

        this.options = fields.map(f => ({ label: f.displayName, value: f.name }));

    }
}
