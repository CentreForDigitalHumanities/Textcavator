import { Component, OnInit } from '@angular/core';
import { SafeHtml, Title } from '@angular/platform-browser';
import { environment } from '@environments/environment';
import { DialogService } from '@services';
import { pageTitle } from '@utils/app';

@Component({
    selector: 'ia-about',
    templateUrl: './about.component.html',
    styleUrls: ['./about.component.scss'],
    standalone: false
})
export class AboutComponent implements OnInit {
    public appName: string;
    public aboutHtml: SafeHtml;
    public isLoading = false;

    constructor(private dialogService: DialogService, private title: Title) {
    }

    ngOnInit() {
        this.isLoading = true;
        this.appName = environment.appName;
        this.fetchData();
        this.title.setTitle(pageTitle('About'));
    }

    async fetchData() {
        this.aboutHtml = await this.dialogService.getAboutPage(environment.aboutPage);
        this.isLoading = false;
    }

}
