import { CommonModule } from '@angular/common';
import { provideHttpClient, withInterceptorsFromDi, withXsrfConfiguration } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { DatePickerModule } from 'primeng/datepicker';
import { DialogModule } from 'primeng/dialog';
import { TableModule } from 'primeng/table';
import { BalloonDirective } from './balloon/balloon.directive';
import { DatePickerComponent } from './date-picker/date-picker.component';
import { ErrorComponent } from './error/error.component';
import { DropdownModule } from './dropdown/dropdown.module';
import { TabPanelDirective } from './tabs/tab-panel.directive';
import { TabsComponent } from './tabs/tabs.component';
import { ToggleComponent } from './toggle/toggle.component';
import { SlugifyPipe } from './pipes/slugify.pipe';
import { ToggleButtonDirective } from './toggle-button/toggle-button.directive';
import { ConfirmModalComponent } from './confirm-modal/confirm-modal.component';

/** this should be imported by all other modules; provides basic building blocks
 * for the whole application
 */
@NgModule({
    declarations: [
        DatePickerComponent,
        ErrorComponent,
        BalloonDirective,
        TabsComponent,
        TabPanelDirective,
        ToggleComponent,
        SlugifyPipe,
        ToggleButtonDirective,
        ConfirmModalComponent,
    ],
    exports: [
        // shared components
        DatePickerComponent,
        ErrorComponent,
        TabsComponent,
        TabPanelDirective,
        ToggleButtonDirective,
        ConfirmModalComponent,
        // shared modules
        BrowserAnimationsModule,
        BrowserModule,
        CommonModule,
        DropdownModule,
        DialogModule,
        FormsModule,
        FontAwesomeModule,
        BalloonDirective,
        RouterModule,
        TableModule,
        ToggleComponent,
        // Shared pipes
        SlugifyPipe,
    ], imports: [
        BrowserAnimationsModule,
        BrowserModule,
        CommonModule,
        DatePickerModule,
        DialogModule,
        FormsModule,
        TableModule,
        DropdownModule,
        FontAwesomeModule,
        RouterModule,
        ReactiveFormsModule,
    ], providers: [
        SlugifyPipe,
        provideHttpClient(withInterceptorsFromDi(), withXsrfConfiguration({
            cookieName: 'csrftoken',
            headerName: 'X-CSRFToken',
        }))
    ] })
export class SharedModule {}
