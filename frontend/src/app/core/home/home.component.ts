import { Component, OnInit } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { environment } from '@environments/environment';
import _ from 'lodash';

@Component({
    selector: 'ia-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss'],
    standalone: false
})
export class HomeComponent implements OnInit {
    appTitle = environment.navbarBrand;
    appName = environment.appName;
    appDescription = _.get(environment, 'appDescription', undefined);

    constructor(title: Title) {
        title.setTitle(this.appName);
    }

    ngOnInit() {
    }
}
