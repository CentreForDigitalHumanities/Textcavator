import { NgModule } from '@angular/core';
import { SharedModule } from '@shared/shared.module';
import { ManualNavigationComponent } from './manual-navigation/manual-navigation.component';
import { ManualComponent } from './manual/manual.component';
import { AboutComponent } from './about/about.component';
import { PrivacyComponent } from './privacy/privacy.component';


@NgModule({
    declarations: [
        AboutComponent,
        ManualComponent,
        ManualNavigationComponent,
        PrivacyComponent,
    ],
    imports: [
        SharedModule
    ], exports: [
        AboutComponent,
        ManualComponent,
        PrivacyComponent,
    ]
})
export class AboutModule { }
