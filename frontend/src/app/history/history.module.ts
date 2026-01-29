import { NgModule } from '@angular/core';
import { DownloadModule } from '../download/download.module';
import { DownloadService, QueryService } from '@services';
import { SharedModule } from '@shared/shared.module';
import { DownloadHistoryComponent } from './download-history/download-history.component';
import {
    QueryFiltersComponent,
    QueryTextPipe,
    SearchHistoryComponent,
} from './search-history';
import { SelectModule } from 'primeng/select';




@NgModule({
    providers: [DownloadService, QueryService],
    declarations: [
        DownloadHistoryComponent,
        QueryFiltersComponent,
        QueryTextPipe,
        SearchHistoryComponent,
    ],
    imports: [DownloadModule, SelectModule, SharedModule],
    exports: [DownloadHistoryComponent, SearchHistoryComponent],
})
export class HistoryModule { }
