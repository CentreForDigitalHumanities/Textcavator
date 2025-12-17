import { Component, ElementRef, OnInit } from '@angular/core';
import { SafeHtml, Title } from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';

import { DialogService } from '@services';
import { pageTitle } from '@utils/app';
import * as _ from 'lodash';

@Component({
    selector: 'ia-manual',
    templateUrl: './manual.component.html',
    styleUrls: ['./manual.component.scss'],
    standalone: false
})
export class ManualComponent implements OnInit {
    public isLoading = false;
    public title: string | undefined;
    public manualHtml: SafeHtml | undefined;


    constructor(
        private dialogService: DialogService,
        private activatedRoute: ActivatedRoute,
        private el: ElementRef<HTMLElement>,
        title: Title
    ) {
        title.setTitle(pageTitle('Manual'));
    }

    ngOnInit() {
        // always close any manual dialog when viewing this page
        this.dialogService.closePage();

        this.activatedRoute.paramMap.subscribe(async params => {
            const identifier = params.get('identifier');
            this.isLoading = true;
            const page = await this.dialogService.getManualPage(identifier);
            this.manualHtml = page.html;
            this.title = page.title;

            this.isLoading = false;

            // if the URL contains a fragment, focus on the matching header
            // does not happen automatically because the content is rendered later
            if (this.activatedRoute.snapshot.fragment) {
                setTimeout(() => this.focusOnFragment(this.activatedRoute.snapshot.fragment));
            }
        });
    }

    private focusOnFragment(fragment) {
        const element = this.el.nativeElement.querySelector<HTMLElement>('#' + fragment);
        if (element) {
            element.tabIndex = -1;
            element.focus();
        }
    }

}
