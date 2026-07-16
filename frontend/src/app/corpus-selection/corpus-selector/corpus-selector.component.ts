import { Component, Input, OnInit } from '@angular/core';
import { Corpus } from '@models';
import { Router } from '@angular/router';
import * as _ from 'lodash';
import { corpusIcons } from '@shared/icons';

@Component({
    selector: 'ia-corpus-selector',
    templateUrl: './corpus-selector.component.html',
    styleUrls: ['./corpus-selector.component.scss'],
    standalone: false
})
export class CorpusSelectorComponent implements OnInit {
    @Input() corpus: Corpus;

    corpusIcons = corpusIcons;

    constructor(private router: Router) { }

    ngOnInit(): void {
    }

    navigateToCorpus(event: any): void {
        if (!event.target.classList.contains('moreInfoLink')) {
            this.router.navigate(['/search', this.corpus.name]);
        }
    }

    backgroundImage(corpus: Corpus) {
        return `url("/api/corpus/image/${corpus.name}")`;
    }
}
