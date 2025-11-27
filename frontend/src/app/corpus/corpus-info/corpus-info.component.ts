import { Component, OnInit } from '@angular/core';
import { ApiService, CorpusService } from '@services';
import { Corpus, CorpusDocumentationPage, FieldCoverage } from '@models';
import { marked } from 'marked';
import { Observable } from 'rxjs';
import { Title } from '@angular/platform-browser';
import { pageTitle } from '@utils/app';
import { map } from 'rxjs/operators';
import * as _ from 'lodash';

@Component({
    selector: 'ia-corpus-info',
    templateUrl: './corpus-info.component.html',
    styleUrls: ['./corpus-info.component.scss'],
    standalone: false
})
export class CorpusInfoComponent implements OnInit {
    corpus: Corpus;

    fieldCoverage: FieldCoverage;

    documentation$: Observable<CorpusDocumentationPage[]>;

    constructor(
        private corpusService: CorpusService,
        private apiService: ApiService,
        private title: Title,
    ) { }

    ngOnInit(): void {
        this.corpusService.currentCorpus.subscribe(this.setCorpus.bind(this));
    }

    setCorpus(corpus: Corpus) {
        this.corpus = corpus;
        this.documentation$ = this.apiService.corpusDocumentationPages(corpus.name).pipe(
            map(pages => pages.filter(page => this.includePage(corpus, page))),
            map(pages => _.sortBy(pages, 'index'))
        );
        this.apiService.fieldCoverage(corpus.name).then(
            result => this.fieldCoverage = result
        );
        this.title.setTitle(pageTitle(`About ${corpus.title}`));
    }

    renderMarkdown(content: string): string {
        return marked.parse(content, { async: false });
    }

    private includePage(corpus: Corpus, page: CorpusDocumentationPage): boolean {
        return (page.type !== 'Word models') || corpus.wordModelsPresent;
    }

}
