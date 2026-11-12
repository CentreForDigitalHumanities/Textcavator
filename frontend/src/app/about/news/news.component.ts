import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ApiService } from '@app/services';
import { LoadingComponent } from '@app/shared/loading/loading.component';

@Component({
    selector: 'ia-news',
    imports: [CommonModule, LoadingComponent],
    templateUrl: './news.component.html',
    styleUrl: './news.component.scss',
})
export class NewsComponent {
    private apiService = inject(ApiService);
    data$ = this.apiService.news();
}
