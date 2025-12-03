import { HttpErrorResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { APIEditableCorpus, CorpusDefinition } from '@models/corpus-definition';
import { ApiService, CorpusService } from '@services';
import { actionIcons, formIcons } from '@shared/icons';
import { Subject } from 'rxjs';
import { SlugifyPipe } from '@shared/pipes/slugify.pipe';
import { Title } from '@angular/platform-browser';
import { pageTitle } from '@utils/app';

@Component({
    selector: 'ia-create-definition',
    templateUrl: './create-definition.component.html',
    styleUrls: ['./create-definition.component.scss'],
    standalone: false
})
export class CreateDefinitionComponent {
    actionIcons = actionIcons;
    formIcons = formIcons;

    corpus: CorpusDefinition;

    error: Error;

    reset$ = new Subject<void>();

    newCorpusTitle: string;

    constructor(
        private apiService: ApiService,
        private router: Router,
        private slugify: SlugifyPipe,
        private title: Title,
        private corpusService: CorpusService,
    ) {
        this.corpus = new CorpusDefinition(this.apiService, this.corpusService);
        this.title.setTitle(pageTitle('New corpus'));
    }

    onJSONUpload(data: any) {
        this.corpus.setFromDefinition(data);
    }

    submit() {
        this.corpus.definition = {
            name: this.slugify.transform(this.newCorpusTitle),
            meta: {
                title: this.newCorpusTitle,
                languages: [],
            },
            fields: [],
            source_data: {
                type: 'csv',
            },
        };
        this.corpus.definition.meta.title = this.newCorpusTitle;
        this.saveCorpus();
    }

    saveCorpus(asImport: boolean = false) {
        this.error = undefined;
        this.corpus.save().subscribe({
            next: (result: APIEditableCorpus) => {
                const nextRoute = asImport
                    ? ['/custom-corpora']
                    : ['/custom-corpora', 'edit', result.id];
                this.router.navigate(nextRoute);
            },
            error: (err: HttpErrorResponse) => {
                this.error = err;
            },
        });
    }
}
