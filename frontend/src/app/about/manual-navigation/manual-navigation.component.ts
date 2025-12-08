
import { combineLatest, map, Observable, of, Subject } from 'rxjs';
import { Component, OnInit } from '@angular/core';
import { AuthService, DialogService, ManualSection } from '@services';
import { actionIcons, navIcons } from '@shared/icons';
import * as _ from 'lodash';

@Component({
    selector: 'ia-manual-navigation',
    templateUrl: './manual-navigation.component.html',
    styleUrls: ['./manual-navigation.component.scss'],
    standalone: false
})
export class ManualNavigationComponent implements OnInit {
    navIcons = navIcons;
    actionIcons = actionIcons;

    manifest$ = new Subject<ManualSection[]>();

    permissionValues = {
        canEditCorpus: this.authService.currentUser$.pipe(map(user => user?.isAdmin)),
    };

    constructor(
        private authService: AuthService,
        private dialogService: DialogService
    ) {}


    async ngOnInit() {
        this.manifest$.next(await this.dialogService.getManifest());
    }

    /**
     * checks whether a user has permission to view a manual section
     *
     * This permission system just hides sections from the menu to avoid confusion if the
     * user cannot access the documented feature.
     */
    hasPermission(section: ManualSection): Observable<boolean> {
        if ('permissions' in section) {
            const values = _.pick(this.permissionValues, section.permissions);
            return combineLatest(values).pipe(
                map((values) => _.every(values)),
            );
        } else {
            return of(true);
        }
    }
}
