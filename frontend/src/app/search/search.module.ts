import { NgModule } from '@angular/core';
import { SharedModule } from '@shared/shared.module';
import { PaginationComponent } from './pagination/pagination.component';
import { HighlightSelectorComponent } from './highlight-selector/highlight-selector.component';
import { SearchResultsComponent } from './search-results/search-results.component';
import { SearchComponent } from './search.component';
import { DocumentModule } from '../document/document.module';
import { CorpusModule } from '../corpus/corpus.module';
import { FilterModule } from '../filter/filter.module';
import { DownloadModule } from '../download/download.module';
import { ElasticSearchService, QueryService, SearchService } from '@services';
import { VisualizationModule } from '../visualization/visualization.module';
import { ResultsSortModule } from './results-sort/results-sort.module';
import { SelectFieldComponent } from './select-field/select-field.component';
import { MultiSelectModule } from 'primeng/multiselect';



@NgModule({
    providers: [
        QueryService,
        SearchService,
        ElasticSearchService,
    ],
    declarations: [
        HighlightSelectorComponent,
        PaginationComponent,
        SearchComponent,
        SearchResultsComponent,
        SelectFieldComponent,
    ],
    imports: [
        CorpusModule,
        DocumentModule,
        DownloadModule,
        FilterModule,
        SharedModule,
        VisualizationModule,
        ResultsSortModule,
        MultiSelectModule,
    ],
    exports: [
        SearchComponent,
    ]
})
export class SearchModule { }
