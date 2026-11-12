import { Component, input } from '@angular/core';
import { NewsItem } from '@app/models/news';

@Component({
    selector: 'ia-news-item',
    imports: [],
    templateUrl: './news-item.component.html',
    styleUrl: './news-item.component.scss',
})
export class NewsItemComponent {
    item = input.required<NewsItem>();
}
