import { Component } from '@angular/core';
import { AuthService } from './services/auth.service';

import { environment } from '@environments/environment';

@Component({
    selector: 'ia-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
    standalone: false,
})
export class AppComponent {
    public iframe: boolean;

    constructor(
        private authService: AuthService,
    ) {
        this.authService.setInitialAuth();
        this.iframe = environment.runInIFrame;
    }

}
