import { Component, ElementRef, HostListener, ViewChild } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { Title } from '@angular/platform-browser';
import {
    AuthService,
    CorpusService,
    ParamService,
    WordmodelsService,
} from '@services';
import { visualizationIcons } from '@shared/icons';
import { Corpus, QueryFeedback, WordInModelResult } from '@models';
import { ParamDirective } from '../param/param-directive';
import { pageTitle } from '@utils/app';

@Component({
    selector: 'ia-word-models',
    templateUrl: './word-models.component.html',
    styleUrls: ['./word-models.component.scss'],
    standalone: false
})
export class WordModelsComponent extends ParamDirective {
    @ViewChild('searchSection', { static: false })
    public searchSection: ElementRef;
    public isScrolledDown: boolean;

    corpus: Corpus;

    queryText: string;
    asTable = false;
    palette: string[];

    activeQuery: string;

    currentTab: 'relatedwords' | 'wordsimilarity';
    nullableParameters = ['query', 'show'];

    tabs = {
        relatedwords: {
            title: 'Related words',
            manual: 'relatedwords',
            chartID: 'chart',
        },
        neighbornetwork: {
            title: 'Network of nearest neighbours',
            manual: 'neighbour-network',
            chartID: 'chart',
        },
        wordsimilarity: {
            title: 'Compare similarity',
            manual: 'comparesimilarity',
            chartID: 'chart',
        },
    };

    visualizationIcons = visualizationIcons;

    errorMessage: string;

    queryFeedback: QueryFeedback;

    constructor(
        route: ActivatedRoute,
        router: Router,
        paramService: ParamService,
        private corpusService: CorpusService,
        private authService: AuthService,
        private wordModelsService: WordmodelsService,
        private title: Title,
    ) {
        super(route, router, paramService);
    }

    get imageFileName(): string {
        if (this.currentTab && this.corpus) {
            return `${this.currentTab}_${this.corpus.name}.png`;
        }
    }

    get tabNames() {
        return Object.keys(this.tabs);
    }

    @HostListener('window:scroll', [])
    onWindowScroll() {
        // mark that the search results have been scrolled down and we should some border
        this.isScrolledDown =
            this.searchSection.nativeElement.getBoundingClientRect().y === 0;
    }

    async initialize(): Promise<void> {
        this.corpusService.currentCorpus.subscribe(this.setCorpus.bind(this));
    }

    teardown() {}

    setStateFromParams(params: ParamMap) {
        const queryFromParams = params.get('query');
        if (queryFromParams !== this.activeQuery) {
            this.queryText = queryFromParams;
            this.activeQuery = this.queryText;
            this.validateQuery();
            if (this.queryFeedback === undefined) {
                this.wordModelsService
                    .wordInModel(this.queryText, this.corpus.name)
                    .then(this.handleWordInModel.bind(this))
                    .catch(() => (this.queryFeedback = { status: 'error' }));
            }
            this.activeQuery = this.queryText;
            this.queryFeedback = { status: 'success' };
        }
        if (params.has('show')) {
            this.currentTab = params.get('show') as 'relatedwords' | 'wordsimilarity';
        } else {
            this.currentTab = 'relatedwords';
        }
    }

    setCorpus(corpus: Corpus): void {
        if (corpus && (!this.corpus || this.corpus.name !== corpus.name)) {
            this.corpus = corpus;
            this.title.setTitle(pageTitle(`Word models of ${corpus.title}`));
        }
    }

    submitQuery(): void {
        this.errorMessage = undefined;
        this.setParams({ query: this.queryText });
    }

    validateQuery() {
        if (!this.queryText || !this.queryText.length) {
            this.queryFeedback = { status: 'empty' };
        } else if (this.queryText.includes(' ')) {
            this.queryFeedback = { status: 'multiple words' };
        } else {
            this.queryFeedback = undefined;
        }
    }

    handleWordInModel(result: WordInModelResult) {
        if (result.exists === true) {
            this.queryFeedback = { status: 'success' };
        } else {
            this.queryFeedback = {
                status: 'not in model',
                similarTerms: result.similar_keys,
            };
        }
    }

    setErrorMessage(event: { message: string }): void {
        this.errorMessage = event.message;
    }

    onTabChange(tab: 'relatedwords' | 'wordsimilarity'): void {
        // reset error message on tab switch
        this.errorMessage = undefined;
        this.setParams({ show: tab });
    }
}
