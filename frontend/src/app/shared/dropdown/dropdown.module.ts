import { NgModule } from '@angular/core';
import { DropdownComponent } from './dropdown.component';
import { DropdownItemDirective } from './dropdown-item.directive';
import { DropdownMenuDirective } from './dropdown-menu.directive';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbDropdownModule } from '@ng-bootstrap/ng-bootstrap';
import { DropdownToggleDirective } from './dropdown-toggle.directive';

@NgModule({
    declarations: [
        DropdownComponent,
        DropdownMenuDirective,
        DropdownItemDirective,
        DropdownToggleDirective,
    ],
    imports: [
        CommonModule,
        FontAwesomeModule,
        NgbDropdownModule
    ],
    exports: [
        DropdownComponent,
        DropdownMenuDirective,
        DropdownItemDirective,
        DropdownToggleDirective,
    ]
})
export class DropdownModule { };
