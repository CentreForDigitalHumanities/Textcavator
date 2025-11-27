import { NgModule } from '@angular/core';
import { SharedModule } from '@shared/shared.module';
import { CorpusHeaderComponent } from './corpus-header/corpus-header.component';
import { CorpusService } from '@services';
import { RouterModule } from '@angular/router';
import { CorpusInfoComponent } from './corpus-info/corpus-info.component';
import { FieldInfoComponent } from './corpus-info/field-info/field-info.component';



@NgModule({
    providers: [
        CorpusService
    ],
    declarations: [
        CorpusHeaderComponent,
        CorpusInfoComponent,
        FieldInfoComponent,
    ],
    imports: [
        SharedModule,
        RouterModule,
    ], exports: [
        CorpusHeaderComponent,
        CorpusInfoComponent,
    ]
})
export class CorpusModule { }
