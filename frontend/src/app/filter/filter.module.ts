import { NgModule } from '@angular/core';
import { CheckboxModule } from 'primeng/checkbox';
import { MultiSelectModule } from 'primeng/multiselect';
import { SliderModule } from 'primeng/slider';
import {
    AdHocFilterComponent,
    BooleanFilterComponent,
    DateFilterComponent,
    FilterBoxComponent,
    MultipleChoiceFilterComponent,
    RangeFilterComponent,
    TagFilterComponent,
} from '.';
import { SearchService } from '@services';
import { SharedModule } from '@shared/shared.module';
import { FilterManagerComponent } from './filter-manager/filter-manager.component';




@NgModule({
    providers: [
        SearchService,
    ],
    declarations: [
        AdHocFilterComponent,
        BooleanFilterComponent,
        DateFilterComponent,
        FilterManagerComponent,
        MultipleChoiceFilterComponent,
        RangeFilterComponent,
        FilterBoxComponent,
        TagFilterComponent,
    ],
    imports: [
        CheckboxModule,
        MultiSelectModule,
        SharedModule,
        SliderModule,
    ],
    exports: [
        FilterManagerComponent,
    ]
})
export class FilterModule { }
