import { Component } from '@angular/core';

import { environment } from '@environments/environment';
import { ThemeService } from '@services/theme.service';

@Component({
    selector: 'ia-footer',
    templateUrl: './footer.component.html',
    styleUrls: ['./footer.component.scss'],
    standalone: false
})
export class FooterComponent {
    environment = environment as any;
    theme$ = this.themeService.theme$;

    constructor(
        private themeService: ThemeService
    ) { }
}
