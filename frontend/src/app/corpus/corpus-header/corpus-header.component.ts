import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { Corpus } from '@models';
import { corpusIcons } from '@shared/icons';

@Component({
    selector: 'ia-corpus-header',
    templateUrl: './corpus-header.component.html',
    styleUrls: ['./corpus-header.component.scss'],
    standalone: false
})
export class CorpusHeaderComponent implements OnChanges, OnInit {
    @Input() corpus: Corpus;
    @Input() currentPage: 'search'|'word-models'|'document'|'info';

    corpusIcons = corpusIcons;

    wordModelsPresent: boolean;

    constructor() {
    }

    ngOnInit() {
        window.scrollTo(0,0);
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (this.corpus) {
            this.wordModelsPresent = this.corpus.wordModelsPresent;
        }
    }
}
