import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CorpusDefinition } from '@models/corpus-definition';
import { ApiService } from '@services/api.service';
import { CorpusDefinitionService } from '../../corpus-definition.service';
import { combineLatest, map, tap } from 'rxjs';
import _ from 'lodash';
import { actionIcons, corpusIcons } from '@shared/icons';
import { Title } from '@angular/platform-browser';
import { pageTitle } from '@utils/app';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CorpusService } from '@app/services';

@Component({
    selector: 'ia-corpus-form',
    templateUrl: './corpus-form.component.html',
    styleUrl: './corpus-form.component.scss',
    providers: [CorpusDefinitionService],
    standalone: false
})
export class CorpusFormComponent {
    steps$ = this.corpusDefService.steps$.asObservable();
    activeStep$ = this.corpusDefService.activeStep$.asObservable();

    nextStep$ = combineLatest([this.steps$, this.activeStep$]).pipe(
        map(([steps, current]) => _.nth(steps, current + 1)),
    );

    corpus$ = this.corpusDefService.corpus$.asObservable();

    actionIcons = actionIcons;
    corpusIcons = corpusIcons;

    constructor(
        private apiService: ApiService,
        private route: ActivatedRoute,
        private corpusDefService: CorpusDefinitionService,
        private corpusService: CorpusService,
        private title: Title,
    ) {
        const id = parseInt(this.route.snapshot.params['corpusID'], 10);
        const fetchedCorpus = new CorpusDefinition(this.apiService, this.corpusService, id);
        this.corpusDefService.setCorpus(fetchedCorpus);
        fetchedCorpus.definitionUpdated$.pipe(
            takeUntilDestroyed(),
        ).subscribe(() => {
            const corpusTitle = fetchedCorpus.definition.meta.title;
            this.title.setTitle(pageTitle(`${corpusTitle}: edit`));
        });
    }

    onActiveIndexChange(event: number) {
        this.corpusDefService.activateStep(event);
    }

    toNext() {
        this.corpusDefService.activateStep(this.corpusDefService.activeStep$.value + 1);
    }
}
