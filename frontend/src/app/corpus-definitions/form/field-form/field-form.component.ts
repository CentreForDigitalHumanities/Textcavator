import { Component, ElementRef, Input, OnChanges, SimpleChanges } from '@angular/core';
import { FormArray, FormControl, FormGroup, Validators } from '@angular/forms';
import {
    APICorpusDefinitionField,
    CorpusDataFile,
    CorpusDefinition,
    DataFileFieldInfo,
    FIELD_TYPE_OPTIONS,
    FieldDataType,
} from '@models/corpus-definition';
import { MenuItem } from 'primeng/api';
import { catchError, combineLatest, map, Observable, of, shareReplay, startWith, Subject, take, takeUntil, tap } from 'rxjs';
import * as _ from 'lodash';

import { collectLanguages, Language } from '../constants';
import { actionIcons, directionIcons, formIcons } from '@shared/icons';
import { mergeAsBooleans } from '@utils/observables';
import { ApiService, DialogService } from '@services';
import { CorpusDefinitionService } from '@app/corpus-definitions/corpus-definition.service';
import { findByName } from '@app/utils/utils';

type FieldFormGroup = FormGroup<{
    display_name: FormControl<string>,
    description: FormControl<string>,
    type: FormControl<FieldDataType>,
    options: FormGroup<{
        search: FormControl<boolean>,
        filter: FormControl<boolean>,
        preview: FormControl<boolean>,
        visualize: FormControl<boolean>,
        sort: FormControl<boolean>,
        hidden: FormControl<boolean>,
    }>,
    language: FormControl<Language>,
    name: FormControl<string>,
    extract: FormGroup<{
        column: FormControl<string>,
    }>,
}>;

const allLanguages = collectLanguages();

const UNKNOWN_LANGUAGE = { code: '', displayName: 'Unknown', altNames: ''};

@Component({
    selector: 'ia-field-form',
    templateUrl: './field-form.component.html',
    styleUrl: './field-form.component.scss',
    standalone: false
})
export class FieldFormComponent implements OnChanges {
    @Input({ required: true }) corpus!: CorpusDefinition;
    destroy$ = new Subject<void>();

    fieldsForm = new FormGroup({
        fields: new FormArray<FieldFormGroup>([]),
    });

    fieldTypeOptions: MenuItem[] = FIELD_TYPE_OPTIONS;

    languageOptions: Language[] = [];

    actionIcons = actionIcons;
    directionIcons = directionIcons;
    formIcons = formIcons;

    valueChange$ = new Subject<void>();
    validationFailed$ = new Subject<void>();
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
    showValidationMessage$: Observable<boolean> = mergeAsBooleans({
        true: [this.validationFailed$],
        false: [this.fieldsForm.valueChanges, this.changesSubmitted$],
    });
    showErrorMessage$: Observable<boolean> = mergeAsBooleans({
        true: [this.changesSavedError$],
        false: [this.valueChange$, this.changesSubmitted$],
    });

    dataFile$: Observable<CorpusDataFile | undefined>;
    unusedCsvFields$: Observable<DataFileFieldInfo[]>;

    constructor(
        private el: ElementRef<HTMLElement>,
        private dialogService: DialogService,
        private apiService: ApiService,
        private corpusDefService: CorpusDefinitionService,
    ) {}

    get fields(): FormArray<FieldFormGroup> {
        return this.fieldsForm.get('fields') as FormArray;
    }

    makeFieldFormgroup(
        field: APICorpusDefinitionField, corpusIsActive: boolean
    ): FieldFormGroup {
        let fg = this.fieldToForm(field);
        if (corpusIsActive) {
            this.disableControls(fg);
        }

        fg.controls.type.valueChanges.pipe(
            takeUntil(this.destroy$),
        ).subscribe(() =>
            this.onFieldTypeChange(fg)
        );

        fg.valueChanges.pipe(
            takeUntil(this.destroy$),
        ).subscribe(() => this.valueChange$.next());

        return fg;
    }


    getFieldProperty(field: FieldFormGroup, prop: string) {
        const fieldType = field.get('type').value;
        const option = _.find(this.fieldTypeOptions, { value: fieldType });
        return option[prop];
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.corpus) {
            this.dataFile$ = this.apiService.listDataFiles(this.corpus.id).pipe(
                map(files => files.find(file => file.confirmed)),
                catchError(() => of(undefined)),
                shareReplay(1),
            );
            const formValue$ = this.fieldsForm.valueChanges.pipe(
                startWith(() => undefined),
                map(() => this.fieldsForm.getRawValue())
            );
            this.unusedCsvFields$ = combineLatest([
                this.dataFile$,
                formValue$
            ]).pipe(
                map(([file, formValue]) => {
                    const csvFields = file.csv_info.fields;
                    const formFields = formValue.fields.map(field => field.extract.column);
                    const filtered = csvFields.filter(field => !formFields.includes(field.name));
                    return filtered;
                })
            );
            this.corpus.definitionUpdated$
            .pipe(takeUntil(this.destroy$))
                .subscribe(() => {
                    this.languageOptions = this.getLanguageOptions();
                    this.fieldsForm.controls.fields = new FormArray(
                        this.corpus.definition.fields.map(
                            field => this.makeFieldFormgroup(field, this.corpus.active)
                        )
                    );
                    this.fieldsForm.updateValueAndValidity();
                });
        }
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    onSubmit(): void {
        if (this.fieldsForm.valid) {
            this.changesSubmitted$.next();
            const newFields = this.fields.controls.map(fg => this.formToField(fg));
            this.corpus.definition.fields = newFields;
            this.corpus.save().subscribe({
                next: () => this.changesSavedSucces$.next(),
                error: (err) => {
                    this.changesSavedError$.next();
                    console.error(err);
                },
            });
        } else {
            this.onValidationFail();
        }
    }

    /** identifier for a field control
     *
     * includes the index as an argument so this can be used as a TrackByFunction
     */
    fieldControlName(index: number, field: FieldFormGroup) {
        return field.get('extract').get('column').value as string;
    }

    moveField(index: number, field: FieldFormGroup, delta: number): void {
        this.fields.removeAt(index);
        this.fields.insert(index + delta, field);

        // after change detection, restore focus to the button
        setTimeout(() => this.focusOnMoveControl(index, field, delta));
    }

    moveControlID(index: number, field: FieldFormGroup, delta: number): string {
        const label = delta > 0 ? 'movedown' : 'moveup';
        return label + '-' + this.fieldControlName(index, field);
    }

    focusOnMoveControl(index: number, field: FieldFormGroup, delta: number): void {
        const selector = '#' + this.moveControlID(index, field, delta);
        const button = this.el.nativeElement.querySelector<HTMLButtonElement>(selector);
        button.focus();
    }

    showFieldDocumentation(): void {
        this.dialogService.showManualPage('types-of-fields');
    }

    addField(name: string): void {
        const field$ = this.unusedCsvFields$.pipe(
            take(1),
            map(fields => findByName(fields, name)),
            map(info => this.corpusDefService.makeDefaultField(info.type, info.name))
        );

        field$.subscribe(field => {
            const fg = this.makeFieldFormgroup(field, this.corpus.active);
            this.fieldsForm.controls.fields.push(fg);
            this.fieldsForm.updateValueAndValidity();
        });
    }

    removeField(index: number): void {
        this.fieldsForm.controls.fields.removeAt(index);
        this.fieldsForm.updateValueAndValidity();
    }

    private fieldToForm(field: APICorpusDefinitionField): FieldFormGroup {
        return new FormGroup({
            display_name: new FormControl<string>(
                field.display_name,
                { validators: [Validators.required] }
            ),
            description: new FormControl<string>(field.description),
            type: new FormControl<FieldDataType>(field.type),
            options: new FormGroup({
                search: new FormControl<boolean>(field.options.search),
                filter: new FormControl<boolean>(
                    field.options.filter == 'show'
                ),
                preview: new FormControl<boolean>(field.options.preview),
                visualize: new FormControl<boolean>(field.options.visualize),
                sort: new FormControl<boolean>(field.options.sort),
                hidden: new FormControl<boolean>(field.options.hidden),
            }),
            language: new FormControl<Language>(
                this.languageOptions.find(l => l.code == field.language) || UNKNOWN_LANGUAGE,
                { nonNullable: true },
            ),
            // hidden in the form, but included to ease syncing model with form
            name: new FormControl<string>(field.name),
            extract: new FormGroup({
                column: new FormControl<string>(field.extract.column),
            }),
        });
    }

    private formToField(fg: FieldFormGroup): APICorpusDefinitionField {
        const value = fg.getRawValue();
        return {
            name: value.name,
            description: value.description,
            display_name: value.display_name,
            type: value.type,
            options: {
                search: value.options.search,
                filter: value.options.filter ? 'show' : 'none',
                preview: value.options.preview,
                visualize: value.options.visualize,
                sort: value.options.sort,
                hidden: value.options.hidden,
            },
            language: value.language.code,
            extract: value.extract,
        };
    }

    private onFieldTypeChange(fg: FormGroup): void {
        const dtype = fg.value['type'];
        fg.controls.options.setValue(this.corpusDefService.defaultFieldOptions(dtype));
    }

    private onValidationFail(): void {
        this.fieldsForm.markAllAsTouched();
        this.validationFailed$.next();
    }

    private getLanguageOptions(): Language[] {
        // include corpus languages + interface language
        const languageCodes = this.corpus.definition.meta.languages;
        if (!languageCodes.includes('eng')) {
            languageCodes.push('eng')
        }

        const languages = allLanguages.filter(l => languageCodes.includes(l.code));
        languages.push(UNKNOWN_LANGUAGE);
        return languages;
    }

    private disableControls(form: FormGroup): void {
        form.controls.type.disable();
        form.controls.name.disable();
        form.controls.extract.disable();
        form.controls.language.disable();
        const options = (form.controls.options as FormGroup);
        options.controls.search.disable();
        options.controls.filter.disable();
    }
}
