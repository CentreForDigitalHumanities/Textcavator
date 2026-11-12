import { CommonModule } from '@angular/common';
import { Component, computed, input } from '@angular/core';
import { toObservable } from '@angular/core/rxjs-interop';
import { NewsItem } from '@app/models/news';
import { marked } from 'marked';
import { switchMap } from 'rxjs';

@Component({
    selector: 'ia-news-item',
    imports: [CommonModule],
    templateUrl: './news-item.component.html',
    styleUrl: './news-item.component.scss',
})
export class NewsItemComponent {
    item = input.required<NewsItem>();

    content$ = toObservable(this.item).pipe(
        switchMap(item => Promise.resolve(marked.parse(item.content))),
    );

    date = computed(() => Date.parse(this.item().date));
}
