import { Component } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { APIEditableCorpus } from '@models/corpus-definition';
import { ApiService } from '@services';
import { actionIcons, documentIcons } from '@shared/icons';
import { pageTitle } from '@utils/app';
import { Observable } from 'rxjs';

@Component({
    selector: 'ia-definitions-overview',
    templateUrl: './definitions-overview.component.html',
    styleUrls: ['./definitions-overview.component.scss'],
    standalone: false
})
export class DefinitionsOverviewComponent {
    actionIcons = actionIcons;
    documentIcons = documentIcons;

    corpora$: Observable<APIEditableCorpus[]>;

    handleDelete = this.requestDelete.bind(this);

    constructor(
        private apiService: ApiService,
        private title: Title
    ) {
        this.corpora$ = this.apiService.corpusDefinitions();
        this.title.setTitle(pageTitle('Custom corpora'));
    }

    onDeleteComplete() {
        this.corpora$ = this.apiService.corpusDefinitions();
    }

    private requestDelete(corpus: APIEditableCorpus) {
        return this.apiService.deleteCorpus(corpus.id);
    }
}
