import { Component, OnInit } from '@angular/core';
import { Corpus } from '@models/corpus';
import * as _ from 'lodash';
import { actionIcons } from '@shared/icons';
import { environment } from '@environments/environment';
import { BehaviorSubject } from 'rxjs';
import { showLoading } from '@app/utils/utils';
import { CorpusService } from '@app/services';


@Component({
    selector: 'ia-corpus-selection',
    templateUrl: './corpus-selection.component.html',
    styleUrls: ['./corpus-selection.component.scss'],
    standalone: false
})
export class CorpusSelectionComponent implements OnInit {
    public items: Corpus[];

    filteredItems: Corpus[];

    actionIcons = actionIcons;

    showCorpusFilters = _.get(environment, 'showCorpusFilters', true);

    isLoading = new BehaviorSubject<boolean>(false);

    constructor(private corpusService: CorpusService) { }

    get displayItems(): Corpus[] {
        if (_.isUndefined(this.filteredItems)) {
            return this.items;
        } else {
            return this.filteredItems;
        }
    }

    ngOnInit() {
        showLoading(
            this.isLoading,
            this.corpusService.get(true).then((items) => (this.items = items))
        );

    }
}
