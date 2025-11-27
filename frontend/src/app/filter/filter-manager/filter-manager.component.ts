/* eslint-disable @typescript-eslint/member-ordering */
import { Component, Input } from '@angular/core';

import * as _ from 'lodash';
import { combineLatest, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { FilterInterface, QueryModel } from '@models/index';
import { filterIcons } from '@shared/icons';
import { AuthService } from '@services/auth.service';
import { isTagFilter } from '@models/tag-filter';

@Component({
    selector: 'ia-filter-manager',
    templateUrl: './filter-manager.component.html',
    styleUrls: ['./filter-manager.component.scss'],
    standalone: false
})
export class FilterManagerComponent {
    @Input() queryModel: QueryModel;

    filterIcons = filterIcons;
    authorized: boolean;

    constructor(private authService: AuthService) {
        this.authorized = this.authService.getCurrentUser() !== null;
    }

    get activeFilters(): FilterInterface[] {
        return this.queryModel?.activeFilters;
    }

    get filters(): FilterInterface[] {
        const filters = this.queryModel?.filters;
        if (this.authorized) {
            return filters;
        } else {
            return filters.filter(filter => !isTagFilter(filter));
        }
    }

    get anyActiveFilters$(): Observable<boolean> {
        if (this.filters) {
            const statuses = this.filters.map(filter => filter.state$);
            return combineLatest(statuses).pipe(
                map(values => _.some(values, state => state.active)),
            );
        }
    }

    get anyNonDefaultFilters$(): Observable<boolean> {
        if (this.filters) {
            const statuses = this.filters.map(filter => filter.isDefault$);
            return combineLatest(statuses).pipe(
                map(values => !_.every(values)),
            );
        }
    }

    public toggleActiveFilters() {
        if (this.activeFilters.length) {
            this.filters.forEach(filter => filter.deactivate());
        } else {
            this.filters.forEach(filter => filter.activate());
        }
    }

    public resetAllFilters() {
        this.filters.forEach(filter => {
            filter.reset();
        });
    }

}
