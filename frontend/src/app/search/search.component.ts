import { Component, ElementRef, HostListener, OnDestroy, OnInit, ViewChild } from '@angular/core';
import * as _ from 'lodash';
import { Subscription } from 'rxjs';

import { Corpus, CorpusField, QueryModel, User } from '@models/index';
import { CorpusService, DialogService } from '@services/index';

import { AuthService } from '@services/auth.service';
import { distinct, filter } from 'rxjs/operators';
import { actionIcons, navIcons, searchIcons } from '@shared/icons';
import { RouterStoreService } from '../store/router-store.service';
import { Title } from '@angular/platform-browser';
import { SearchTab, SearchTabs } from './search-tabs';
import { environment } from '@environments/environment';
import { pageTitle } from '@utils/app';

@Component({
    selector: 'ia-search',
    templateUrl: './search.component.html',
    styleUrls: ['./search.component.scss'],
    standalone: false
})
export class SearchComponent implements OnInit, OnDestroy {
    @ViewChild('searchSection', { static: false })
    public searchSection: ElementRef;

    public isScrolledDown: boolean;

    public corpus: Corpus;

    public user: User;

    searchIcons = searchIcons;
    actionIcons = actionIcons;

    public queryModel: QueryModel;
    /**
     * This is the query text currently entered in the interface.
     */
    public queryText: string;

    public filterFields: CorpusField[] = [];

    public nullableParameters = [];

    tabs: SearchTabs;

    protected corpusSubscription: Subscription;

    /**
     * This is a constant used to ensure that, when we are displayed in an iframe,
     * the filters are displayed even if there are no results.
     */
    private minIframeHeight = 1300;

    constructor(
        private authService: AuthService,
        private corpusService: CorpusService,
        private dialogService: DialogService,
        private routerStoreService: RouterStoreService,
        private title: Title,
    ) {
        this.tabs = new SearchTabs(this.routerStoreService);
    }

    @HostListener('window:scroll', [])
    onWindowScroll() {
        // mark that the search results have been scrolled down and we should some border
        this.isScrolledDown =
            this.searchSection.nativeElement.getBoundingClientRect().y === 0;
    }

    ngOnInit() {
        this.authService.getCurrentUserPromise().then(user => this.user = user);
        this.corpusSubscription = this.corpusService.currentCorpus
            .pipe(
                filter((corpus) => !!corpus),
                distinct(corpus => corpus.name),
            )
            .subscribe((corpus) => {
                this.setCorpus(corpus);
            });

        if (window.parent) {
            // iframe support
            window.parent.postMessage(['setHeight', this.minIframeHeight], '*');
        }
    }

    ngOnDestroy() {
        this.user = undefined;
        this.corpusSubscription.unsubscribe();
        this.queryModel.complete();
    }

    public showQueryDocumentation() {
        this.dialogService.showManualPage('query');
    }

    public search() {
        this.queryModel.setQueryText(this.queryText);
    }

    onTabChange(tab: SearchTab) {
        this.tabs.setParams({tab});
    }

    private setCorpus(corpus: Corpus) {
        this.corpus = corpus;
        this.setQueryModel();
        this.title.setTitle(pageTitle(`Search ${corpus.title}`));
    }

    private setQueryModel() {
        if (this.queryModel) {
            this.queryModel.complete();
        }
        this.queryModel = new QueryModel(this.corpus, this.routerStoreService);
        this.queryText = this.queryModel.queryText;
    }
}
