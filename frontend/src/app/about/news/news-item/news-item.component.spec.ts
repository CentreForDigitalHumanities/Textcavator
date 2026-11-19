import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewsItemComponent } from './news-item.component';
import { NewsItem } from '@app/models/news';

describe('NewsItemComponent', () => {
    let component: NewsItemComponent;
    let fixture: ComponentFixture<NewsItemComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [NewsItemComponent]
        })
            .compileComponents();

        fixture = TestBed.createComponent(NewsItemComponent);
        const item: NewsItem = {
            id: 1,
            date: '2026-01-01',
            title: 'Test',
            content: 'This is a test message.'
        }
        fixture.componentRef.setInput('item', item);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
