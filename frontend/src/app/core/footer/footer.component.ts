import { Component } from '@angular/core';

import { environment } from '@environments/environment';

@Component({
    selector: 'ia-footer',
    templateUrl: './footer.component.html',
    styleUrls: ['./footer.component.scss'],
    standalone: false
})
export class FooterComponent {
    environment = environment as any;

    constructor() { }

}
