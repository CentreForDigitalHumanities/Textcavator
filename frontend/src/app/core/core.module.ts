import { NgModule } from '@angular/core';
import { SharedModule } from '@shared/shared.module';
import { HomeComponent } from './home/home.component';
import { MenuComponent } from './menu/menu.component';
import { NotificationsComponent } from './notifications/notifications.component';
import { MenuDropdownComponent } from './menu/menu-dropdown/menu-dropdown.component';
import { FooterComponent } from './footer/footer.component';
import { DialogComponent } from './dialog/dialog.component';
import { CorpusSelectionModule } from '../corpus-selection/corpus-selection.module';
import { AlertComponent } from './alert/alert.component';
import { ThemeButtonComponent } from '@app/core/menu/theme-button/theme-button.component';


/** toplevel components such as the home page and navbar */
@NgModule({
    declarations: [
        DialogComponent,
        FooterComponent,
        HomeComponent,
        MenuComponent,
        MenuDropdownComponent,
        NotificationsComponent,
        AlertComponent,
        ThemeButtonComponent,
    ],
    imports: [SharedModule, CorpusSelectionModule],
    exports: [
        AlertComponent,
        DialogComponent,
        FooterComponent,
        MenuComponent,
        NotificationsComponent,
    ],
})
export class CoreModule {}
