import { Component, } from '@angular/core';
import { actionIcons, formIcons } from '@shared/icons';
import { Subject } from 'rxjs';
import { CorpusDefinition } from '@models/corpus-definition';
import { ApiService, CorpusService } from '@services';
import { ActivatedRoute } from '@angular/router';
import * as _ from 'lodash';
import { HttpErrorResponse } from '@angular/common/http';
import { Title } from '@angular/platform-browser';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { pageTitle } from '@utils/app';
import { environment } from '@environments/environment';

@Component({
    selector: 'ia-definition-in-out',
    templateUrl: './definition-in-out.component.html',
    styleUrls: ['./definition-in-out.component.scss'],
    standalone: false
})
export class DefinitionInOutComponent {
    actionIcons = actionIcons;
    formIcons = formIcons;
    appName = environment.appName;

    reset$: Subject<void> = new Subject();

    corpus: CorpusDefinition;

    error: Error;


    constructor(
        private apiService: ApiService,
        private corpusService: CorpusService,
        private route: ActivatedRoute,
        private title: Title,
    ) {
        const id = parseInt(this.route.snapshot.params['corpusID'], 10);
        this.corpus = new CorpusDefinition(this.apiService, this.corpusService, id);
        this.corpus.definitionUpdated$.pipe(
            takeUntilDestroyed(),
        ).subscribe(() => {
            const corpusTitle = this.corpus.definition.meta.title;
            this.title.setTitle(pageTitle(`${corpusTitle}: import/export`));
        });
    }

    downloadJSON() {
        const data = this.corpus.toDefinition();
        const content = JSON.stringify(data, undefined, 4);
        const blob = new Blob([content], {
            type: `application/json;charset=utf-8`,
            endings: 'native',
        });
        const filename = data.name + '.json';
        saveAs(blob, filename);
    }

    onJSONUpload(data: any) {
        this.corpus.setFromDefinition(data);
    }

    submit() {
        this.corpus.save().subscribe({
            next: () => this.reset(),
            error: (err: HttpErrorResponse) => {this.error = err; this.reset()}
        });
    }

    reset() {
        this.reset$.next();
    }
}
