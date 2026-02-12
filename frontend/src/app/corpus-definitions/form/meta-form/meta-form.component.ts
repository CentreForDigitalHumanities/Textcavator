import {
    Component,
    Input,
    OnChanges,
    OnDestroy, SimpleChanges
} from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { map, Observable, Subject, takeUntil, take } from 'rxjs';
import { CorpusDefinitionService } from '../../corpus-definition.service';
import { APICorpusDefinition, APIEditableCorpus, CorpusDefinition } from '../../../models/corpus-definition';
import { collectLanguages, Language } from '../constants';
import { actionIcons, formIcons } from '@shared/icons';
import { mergeAsBooleans } from '@utils/observables';
import { MenuItem } from 'primeng/api';
import _ from 'lodash';

@Component({
    selector: 'ia-meta-form',
    templateUrl: './meta-form.component.html',
    styleUrl: './meta-form.component.scss',
    standalone: false
})
export class MetaFormComponent implements OnChanges, OnDestroy {
    @Input({required: true}) corpus!: CorpusDefinition;

    categories = [
        { value: 'parliament', label: 'Parliamentary debates' },
        { value: 'periodical', label: 'Newspapers and other periodicals' },
        { value: 'finance', label: 'Financial reports' },
        { value: 'ruling', label: 'Laws and rulings' },
        { value: 'review', label: 'Reviews and discussions' },
        { value: 'inscription', label: 'Funerary inscriptions' },
        { value: 'oration', label: 'Orations' },
        { value: 'book', label: 'Books' },
        { value: 'letter', label: 'Letters and life writing' },
        { value: 'poetry', label: 'Poetry and songs' },
        { value: 'social', label: 'Social media' },
        { value: 'informative', label: 'Informative' },
        { value: undefined, label: 'Other' },
    ];

    metaForm = this.formBuilder.group({
        title: [''],
        description: [''],
        category: [''],
        date_range: this.formBuilder.group({
            min: [],
            max: [],
        }),
        languages: [[]],
    });

    destroy$ = new Subject<void>();

    // languageOptions = collectLanguages();
    actionIcons = actionIcons;
    formIcons = formIcons;

    nextStep$: Observable<MenuItem> = this.corpusDefService.steps$.pipe(
        map(steps => steps[1]),
    );

    changesSubmitted$ = new Subject<void>();
    changesSavedSucces$ = new Subject<void>();
    changesSavedError$ = new Subject<void>();

    loading$: Observable<boolean> = mergeAsBooleans({
        true: [this.changesSubmitted$],
        false: [this.changesSavedSucces$, this.changesSavedError$],
    });
    showSuccessMessage$: Observable<boolean> = mergeAsBooleans({
        true: [this.changesSavedSucces$],
        false: [this.metaForm.valueChanges, this.changesSubmitted$],
    });

    showErrorMessage$: Observable<boolean> = mergeAsBooleans({
        true: [this.changesSavedError$],
        false: [this.metaForm.valueChanges, this.changesSubmitted$]
    });

    languages: Language[] = collectLanguages();
    languageSuggestions = this.languages;

    constructor(
        private formBuilder: FormBuilder,
        private corpusDefService: CorpusDefinitionService,
    ) {}

    get currentCategoryLabel(): string {
        const value = this.metaForm.controls.category.value;
        const item = this.categories.find(item => item.value == value);
        return item?.label;
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.corpus) {
            this.corpus.definitionUpdated$
            .pipe(
                take(1),
                takeUntil(this.destroy$)
            )
            .subscribe(() => {
                if (this.corpus.active) {
                    this.metaForm.controls.title.disable();
                } else {
                    this.metaForm.controls.title.enable();
                }
                this.metaForm.patchValue(this.dataToFormValue(this.corpus.definition.meta))
            });
        }
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    onSubmit(): void {
        this.changesSubmitted$.next();
        const newMeta = this.formValueToData(this.metaForm.value);
        this.corpus.definition.meta = newMeta;
        this.corpus.save().subscribe({
            next: this.onSubmitSuccess.bind(this),
            error: this.onSubmitError.bind(this),
        });
    }

    goToNextStep() {
        this.corpusDefService.activateStep(1);
    }

    setLanguageSuggestions(query: string) {
        this.languageSuggestions = this.languages.filter(lang =>
            this.languageMatchesQuery(lang, query)
        );
    }

    private onSubmitSuccess(value: APIEditableCorpus) {
        this.metaForm.patchValue(this.dataToFormValue(value.definition.meta));
        this.changesSavedSucces$.next();
    }

    private onSubmitError(err) {
        this.changesSavedError$.next();
        console.error(err);
    }

    private dataToFormValue(data: APICorpusDefinition['meta']): typeof this.metaForm['value'] {
        const value = _.clone(data) as any;
        value.languages = data.languages.map(code =>
            this.languages.find(l => l.code == code)
        ).filter(_.negate(_.isUndefined));
        return value;
    }

    private formValueToData(value: typeof this.metaForm['value']): APICorpusDefinition['meta'] {
        const data = _.clone(value) as any;
        data.languages = (value.languages || []).map(lang => lang.code);
        return data;
    }

    private languageMatchesQuery(lang: Language, query: string) {
        return this.contains(lang.displayName, query) || this.contains(lang.altNames, query);
    }

    private contains(s: string, query: string) {
        return s.toLowerCase().includes(query.toLowerCase());
    }
}
