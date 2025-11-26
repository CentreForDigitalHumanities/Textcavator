import { APP_BASE_HREF } from '@angular/common';
import { NgModule } from '@angular/core';
import { ExtraOptions, RouterModule, Routes } from '@angular/router';

import { providePrimeNG } from 'primeng/config';
import { CookieService } from 'ngx-cookie-service';
import { DialogModule } from 'primeng/dialog';
import { MenuModule } from 'primeng/menu';
import { environment } from '@environments/environment';


import { ApiRetryService } from './services/index';

import { AboutComponent } from './about/about/about.component';
import { AppComponent } from './app.component';
import { CorpusDefinitionsModule } from './corpus-definitions/corpus-definitions.module';
import { CreateDefinitionComponent } from './corpus-definitions/create-definition/create-definition.component';
import { DefinitionsOverviewComponent } from './corpus-definitions/definitions-overview/definitions-overview.component';
import { DefinitionInOutComponent } from './corpus-definitions/definition-in-out/definition-in-out.component';
import { CorpusFormComponent } from './corpus-definitions/form/corpus-form/corpus-form.component';
import { CorpusModule } from './corpus/corpus.module';
import { CorpusInfoComponent } from './corpus/corpus-info/corpus-info.component';
import { CorpusSelectionModule } from './corpus-selection/corpus-selection.module';
import { CorpusGuard } from './routing/corpus.guard';
import { DocumentPageComponent } from './document/document-page/document-page.component';
import { DocumentModule } from './document/document.module';
import { forwardLegacyParamsGuard } from './routing/forward-legacy-params.guard';
import { DownloadHistoryComponent } from './history/download-history/download-history.component';
import { HistoryModule } from './history/history.module';
import { SearchHistoryComponent } from './history/search-history/index';
import { HomeComponent } from './core/home/home.component';
import { LoggedOnGuard } from './routing/logged-on.guard';
import { LoginComponent } from './login/login.component';
import { LoginModule } from './login/login.module';
import { RegistrationComponent } from './login/registration/registration.component';
import { RequestResetComponent } from './login/reset-password/request-reset.component';
import { ResetPasswordComponent } from './login/reset-password/reset-password.component';
import { VerifyEmailComponent } from './login/verify-email/verify-email.component';
import { ManualComponent } from './about/manual/manual.component';
import { AboutModule } from './about/about.module';
import { PrivacyComponent } from './about/privacy/privacy.component';
import { SearchComponent } from './search/index';
import { SearchModule } from './search/search.module';
import { SettingsComponent } from './settings/settings.component';
import { SettingsModule } from './settings/settings.module';
import { SharedModule } from './shared/shared.module';
import { TagOverviewComponent } from './tag/tag-overview/tag-overview.component';
import { WordModelsComponent } from './word-models/word-models.component';
import { WordModelsModule } from './word-models/word-models.module';
import { MatomoConfig, matomoImports } from './routing/matomo';
import { stylePreset } from './primeng-theme';
import { CoreModule } from './core/core.module';

export const appRoutes: Routes = [
    {
        path: 'search/:corpus',
        component: SearchComponent,
        canActivate: [CorpusGuard, forwardLegacyParamsGuard],
    },
    {
        path: 'word-models/:corpus',
        component: WordModelsComponent,
        canActivate: [CorpusGuard, forwardLegacyParamsGuard],
    },
    {
        path: 'info/:corpus',
        component: CorpusInfoComponent,
        canActivate: [CorpusGuard],
    },
    {
        path: 'document/:corpus/:id',
        component: DocumentPageComponent,
        canActivate: [CorpusGuard],
    },
    {
        path: 'login',
        component: LoginComponent,
    },
    {
        path: 'login/:activated',
        component: LoginComponent,
    },
    {
        path: 'registration',
        component: RegistrationComponent,
    },
    {
        path: 'reset',
        component: RequestResetComponent,
    },
    {
        path: 'reset-password/:uid/:token',
        component: ResetPasswordComponent,
    },
    {
        path: 'privacy',
        component: PrivacyComponent,
    },
    {
        path: 'home',
        component: HomeComponent,
    },
    {
        path: 'manual/:identifier',
        component: ManualComponent,
    },
    {
        path: 'about',
        component: AboutComponent,
    },
    {
        path: 'search-history',
        component: SearchHistoryComponent,
        canActivate: [LoggedOnGuard],
    },
    {
        path: 'download-history',
        component: DownloadHistoryComponent,
        canActivate: [LoggedOnGuard],
    },
    {
        path: 'confirm-email/:key',
        component: VerifyEmailComponent,
    },
    {
        path: 'settings',
        component: SettingsComponent,
        canActivate: [LoggedOnGuard],
    },
    {
        path: 'tags',
        component: TagOverviewComponent,
        canActivate: [LoggedOnGuard],
    },
    {
        path: 'custom-corpora',
        canActivate: [LoggedOnGuard],
        children: [
            {
                path: 'new',
                component: CreateDefinitionComponent,
            },
            {
                path: 'io/:corpusID',
                component: DefinitionInOutComponent,
            },
            {
                path: 'edit/:corpusID',
                component: CorpusFormComponent,
            },
            {
                path: '',
                component: DefinitionsOverviewComponent,
            },
        ],
    },
    {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full',
    },
];

const routerOptions: ExtraOptions = {
    scrollPositionRestoration: 'disabled',
    anchorScrolling: 'enabled',
};

export const imports: any[] = [
    SharedModule,
    // Feature Modules
    CoreModule,
    CorpusModule,
    CorpusDefinitionsModule,
    DialogModule,
    DocumentModule,
    HistoryModule,
    LoginModule,
    AboutModule,
    MenuModule,
    SearchModule,
    SettingsModule,
    WordModelsModule,
    RouterModule.forRoot(appRoutes, routerOptions),
];

if ('matomo' in environment) {
    imports.push(...matomoImports(environment.matomo as MatomoConfig));
}

export const providers: any[] = [
    ApiRetryService,
    CorpusGuard,
    LoggedOnGuard,
    providePrimeNG({
        theme: {
            preset: stylePreset,
            options: {
                darkModeSelector: '[data-theme="dark"]'
            },
        }
    }),
    CookieService,
    { provide: APP_BASE_HREF, useValue: '/' },
];

@NgModule({
    declarations: [AppComponent],
    imports,
    providers,
    bootstrap: [AppComponent],
})
export class AppModule {}
