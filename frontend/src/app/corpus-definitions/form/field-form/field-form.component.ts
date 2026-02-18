import { Component, ElementRef, Input, OnChanges, SimpleChanges } from '@angular/core';
import { FormArray, FormControl, FormGroup, Validators } from '@angular/forms';
import {
    APICorpusDefinitionField,
    CorpusDataFile,
    CorpusDefinition,
    DataFileFieldInfo,
    FIELD_TYPE_OPTIONS,
    FieldDataType,
    FieldFilterSetting,
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
        filter: FormControl<FieldFilterSetting>,
        preview: FormControl<boolean>,
        visualize: FormControl<boolean>,
        sort: FormControl<boolean>,
        hidden: FormControl<boolean>,
    }>,
    language: FormControl<string>,
    name: FormControl<string>,
    extract: FormGroup<{
        column: FormControl<string>,
    }>,
}>;

const allLanguages = collectLanguages();

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
        fields: new FormArray([]),
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

    get fields(): FormArray {
        return this.fieldsForm.get('fields') as FormArray;
    }

    makeFieldFormgroup(
        field: APICorpusDefinitionField, corpusIsActive: boolean
    ): FieldFormGroup {
        let fg: FieldFormGroup = new FormGroup({
            display_name: new FormControl<string>(null, {
                validators: [Validators.required],
            }),
            description: new FormControl<string>(null),
            type: new FormControl<FieldDataType>(null),
            options: new FormGroup({
                search: new FormControl<boolean>(null),
                filter: new FormControl<FieldFilterSetting>(null),
                preview: new FormControl<boolean>(null),
                visualize: new FormControl<boolean>(null),
                sort: new FormControl<boolean>(null),
                hidden: new FormControl<boolean>(null),
            }),
            language: new FormControl<string>(null),
            // hidden in the form, but included to ease syncing model with form
            name: new FormControl<string>(''),
            extract: new FormGroup({
                column: new FormControl<string>(null),
            }),
        });
        fg.patchValue(field);
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
            const newFields = this.fields.getRawValue() as APICorpusDefinitionField[];
            this.corpus.definition.fields =
                newFields as CorpusDefinition['definition']['fields'];
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

    languageLabel(field: FieldFormGroup): string {
        const value = field.controls.language.value;
        return this.languageOptions.find(o => o.code == value)?.displayName;
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

    private onFieldTypeChange(fg: FormGroup): void {
        const dtype = fg.value['type'];
        fg.controls.options.setValue(this.corpusDefService.defaultFieldOptions(dtype));
        fg.controls.language.setValue('');
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
        languages.push({ code: '', displayName: 'Unknown', altNames: ''});
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
