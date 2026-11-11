import { NgModule } from '@angular/core';
import { CheckboxModule } from 'primeng/checkbox';
import { MultiSelectModule } from 'primeng/multiselect';
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
import { RangeSliderComponent } from './range-filter/range-slider/range-slider.component';




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
        RangeSliderComponent
    ],
    exports: [
        FilterManagerComponent,
    ]
})
export class FilterModule { }
