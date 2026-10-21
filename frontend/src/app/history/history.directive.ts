import { Directive } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Corpus, Download, QueryDb } from '@models';
import { CorpusService } from '@services';
import { findByName } from '@utils/utils';

@Directive({
    selector: '[iaHistory]',
    standalone: false
})
export class HistoryDirective {
    corpora: Corpus[];
    corpusMenuItems: MenuItem[];

    constructor(public corpusService: CorpusService) { }

    retrieveCorpora() {
        this.corpusService.get().then((items) => {
            this.corpora = items;
            this.corpusMenuItems = items.map(corpus => ({ label: corpus.title, value: corpus.name }) );
        }).catch(error => {
            console.log(error);
        });
    }

    sortByDate<Item extends Download|QueryDb>(items: Item[]): Item[] {
        return items.sort((a, b) =>
            new Date(b.started).getTime() - new Date(a.started).getTime()
        );
    }


    corpusTitle(corpusName: string): string {
        return findByName(this.corpora, corpusName)?.title || corpusName;
    }
}
