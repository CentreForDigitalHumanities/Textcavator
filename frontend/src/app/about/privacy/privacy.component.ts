import { Component, OnInit } from '@angular/core';
import { SafeHtml, Title } from '@angular/platform-browser';
import { DialogService } from '@services/index';
import { pageTitle } from '@utils/app';

@Component({
    selector: 'ia-privacy',
    templateUrl: './privacy.component.html',
    styleUrls: ['./privacy.component.scss'],
    standalone: false
})
export class PrivacyComponent implements OnInit {
    public header: string | undefined;
    public manualHtml: SafeHtml | undefined;

    constructor(private dialogService: DialogService, private title: Title) {}

    ngOnInit() {
        this.dialogService.getManualPage('privacy').then((page) => {
            this.manualHtml = page.html;
            this.header = page.title;
            this.title.setTitle(pageTitle(this.header));
        });
    }
}
