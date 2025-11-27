import { NgModule } from '@angular/core';
import { SharedModule } from '@shared/shared.module';
import { HomeComponent } from './home/home.component';
import { MenuComponent } from './menu/menu.component';
import { NotificationsComponent } from './notifications/notifications.component';
import { MenuDropdownComponent } from './menu/menu-dropdown/menu-dropdown.component';
import { FooterComponent } from './footer/footer.component';
import { DialogComponent } from './dialog/dialog.component';
import { CorpusSelectionModule } from '../corpus-selection/corpus-selection.module';


/** toplevel components such as the home page and navbar */
@NgModule({
    declarations: [
        DialogComponent,
        FooterComponent,
        HomeComponent,
        MenuComponent,
        MenuDropdownComponent,
        NotificationsComponent,
    ],
    imports: [
        SharedModule,
        CorpusSelectionModule,
    ],
    exports: [
        DialogComponent,
        FooterComponent,
        MenuComponent,
        NotificationsComponent,
    ]
})
export class CoreModule { }
