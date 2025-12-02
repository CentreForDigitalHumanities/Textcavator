import { Component, OnDestroy, OnInit } from '@angular/core';
import {Router} from '@angular/router';
import { SafeHtml } from '@angular/platform-browser';
import { Subscription } from 'rxjs';

import { navIcons } from '@shared/icons';
import { DialogService } from '@services';

@Component({
    selector: 'ia-dialog',
    templateUrl: './dialog.component.html',
    styleUrls: ['./dialog.component.scss'],
    standalone: false
})
export class DialogComponent implements OnDestroy, OnInit {
    public title: string = undefined;
    public innerHtml: SafeHtml | undefined;
    public footerButtonLabel: string;
    public footerRouterLink: string[];
    public showDialog = false;
    public isLoading = false;

    navIcons = navIcons;

    private dialogEventSubscription: Subscription;

    constructor(private dialogService: DialogService, private router: Router) {
        this.dialogEventSubscription = dialogService.pageEvent.subscribe(event => {
            switch (event.status) {
            case 'hide':
                this.innerHtml = undefined;
                this.showDialog = false;
                break;

            case 'loading':
                this.innerHtml = undefined;
                this.showDialog = true;
                this.isLoading = true;
                break;

            case 'show':
                this.innerHtml = event.html;
                this.title = event.title;
                this.showDialog = true;
                this.isLoading = false;
                if (event.footer){
                this.footerButtonLabel = event.footer.buttonLabel;
                this.footerRouterLink = event.footer.routerLink;
                } else {
                this.footerButtonLabel = null;
                }
                break;
            }
        });
    }

    ngOnInit(): void {
        this.dialogService.closePage();
    }

    ngOnDestroy(): void {
        this.dialogEventSubscription.unsubscribe();
    }
}
