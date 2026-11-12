import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewsItemComponent } from './news-item.component';

describe('NewsItemComponent', () => {
    let component: NewsItemComponent;
    let fixture: ComponentFixture<NewsItemComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [NewsItemComponent]
        })
            .compileComponents();

        fixture = TestBed.createComponent(NewsItemComponent);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
