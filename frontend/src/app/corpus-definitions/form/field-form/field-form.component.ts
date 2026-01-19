import { Component, ElementRef, Input, SimpleChanges } from '@angular/core';
import { FormArray, FormControl, FormGroup } from '@angular/forms';
import {
    APICorpusDefinitionField,
    CorpusDefinition,
    FIELD_TYPE_OPTIONS,
} from '@models/corpus-definition';
import { MenuItem } from 'primeng/api';
import { Observable, Subject, takeUntil } from 'rxjs';
import * as _ from 'lodash';

import { collectLanguages, Language } from '../constants';
import { actionIcons, directionIcons, formIcons } from '@shared/icons';
import { mergeAsBooleans } from '@utils/observables';
import { DialogService } from '@services';

const allLanguages = collectLanguages();

@Component({
    selector: 'ia-field-form',
    templateUrl: './field-form.component.html',
    styleUrl: './field-form.component.scss',
    standalone: false
})
export class FieldFormComponent {
    @Input({ required: true }) corpus!: CorpusDefinition;
    destroy$ = new Subject<void>();

    fieldsForm = new FormGroup({
        fields: new FormArray([]),
    });

    fieldTypeOptions: MenuItem[] = FIELD_TYPE_OPTIONS;

    languageOptions: Language[] = [];

    actionIcons = actionIcons;
    directionIcons = directionIcons;
    formIcons = formIcons;

    valueChange$ = new Subject<void>();
    changesSubmitted$ = new Subject<void>();
    changesSavedSucces$ = new Subject<void>();
    changesSavedError$ = new Subject<void>();

    /** show succes message after success response, hide when form is changed or user
     * saves again
     */
    showSuccesMessage$: Observable<boolean> = mergeAsBooleans({
        true: [this.changesSavedSucces$],
        false: [this.valueChange$, this.changesSubmitted$],
    });
    showErrorMessage$: Observable<boolean> = mergeAsBooleans({
        true: [this.changesSavedError$],
        false: [this.valueChange$, this.changesSubmitted$],
    });

    constructor(
        private el: ElementRef<HTMLElement>,
        private dialogService: DialogService,
    ) {}

    get fields(): FormArray {
        return this.fieldsForm.get('fields') as FormArray;
    }

    makeFieldFormgroup(field: APICorpusDefinitionField, corpusIsActive: boolean): FormGroup {
        let fg = new FormGroup({
            display_name: new FormControl(),
            description: new FormControl(),
            type: new FormControl(),
            options: new FormGroup({
                search: new FormControl(),
                filter: new FormControl(),
                preview: new FormControl(),
                visualize: new FormControl(),
                sort: new FormControl(),
                hidden: new FormControl(),
            }),
            language: new FormControl(''),
            // hidden in the form, but included to ease syncing model with form
            name: new FormControl(),
            extract: new FormGroup({
                column: new FormControl(),
            }),
        });
        if (corpusIsActive) {
            this.disableControls(fg);
        }
        fg.patchValue(field);

        fg.valueChanges.pipe(
            takeUntil(this.destroy$),
        ).subscribe(() => this.valueChange$.next());

        return fg;
    }


    getFieldProperty(field: FormGroup, prop: string) {
        const fieldType = field.get('type').value;
        const option = _.find(this.fieldTypeOptions, { value: fieldType });
        return option[prop];
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.corpus) {
            this.corpus.definitionUpdated$
            .pipe(takeUntil(this.destroy$))
                .subscribe(() => {
                    this.languageOptions = this.getLanguageOptions();
                    this.fieldsForm.controls.fields = new FormArray(
                        this.corpus.definition.fields.map(
                            field => this.makeFieldFormgroup(field, this.corpus.active)
                        )
                    );
                });
        }
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    onSubmit(): void {
        const newFields = this.fields.value as APICorpusDefinitionField[];
        this.corpus.definition.fields =
            newFields as CorpusDefinition['definition']['fields'];
        this.corpus.save().subscribe({
            next: () => this.changesSavedSucces$.next(),
            error: (err) => {
                this.changesSavedError$.next();
                console.error(err);
            }

        });
    }

    /** identifier for a field control
     *
     * includes the index as an argument so this can be used as a TrackByFunction
     */
    fieldControlName(index: number, field: FormControl) {
        return field.get('extract').get('column').value as string;
    }

    moveField(index: number, field: FormControl, delta: number): void {
        this.fields.removeAt(index);
        this.fields.insert(index + delta, field);

        // after change detection, restore focus to the button
        setTimeout(() => this.focusOnMoveControl(index, field, delta));
    }

    moveControlID(index: number, field: FormControl, delta: number): string {
        const label = delta > 0 ? 'movedown' : 'moveup';
        return label + '-' + this.fieldControlName(index, field);
    }

    focusOnMoveControl(index: number, field: FormControl, delta: number): void {
        const selector = '#' + this.moveControlID(index, field, delta);
        const button = this.el.nativeElement.querySelector<HTMLButtonElement>(selector);
        button.focus();
    }

    showFieldDocumentation() {
        this.dialogService.showManualPage('types-of-fields');
    }

    languageLabel(field: FormGroup): string {
        const value = field.controls.language.value;
        return this.languageOptions.find(o => o.code == value).displayName;
    }

    private getLanguageOptions() {
        // include corpus languages + interface language
        const languageCodes = this.corpus.definition.meta.languages;
        if (!languageCodes.includes('eng')) {
            languageCodes.push('eng')
        }

        const languages = allLanguages.filter(l => languageCodes.includes(l.code));
        languages.push({ code: '', displayName: 'Unknown', altNames: ''});
        return languages;
    }

    private disableControls(form: FormGroup) {
        form.controls.type.disable();
        form.controls.name.disable();
        form.controls.extract.disable();
        form.controls.language.disable();
        const options = (form.controls.options as FormGroup);
        options.controls.search.disable();
        options.controls.filter.disable();
    }
}
