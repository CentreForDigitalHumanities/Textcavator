import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ApiService } from '@app/services';
import { LoadingComponent } from '@app/shared/loading/loading.component';
import { NewsItemComponent } from './news-item/news-item.component';
import { environment } from '@environments/environment';

@Component({
    selector: 'ia-news',
    imports: [CommonModule, LoadingComponent, NewsItemComponent],
    templateUrl: './news.component.html',
    styleUrl: './news.component.scss',
})
export class NewsComponent {
    private apiService = inject(ApiService);
    data$ = this.apiService.news();
    appName = environment.appName;
}
