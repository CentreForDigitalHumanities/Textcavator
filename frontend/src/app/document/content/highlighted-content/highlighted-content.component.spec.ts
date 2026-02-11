import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HighlightedContentComponent } from './highlighted-content.component';
import { SharedModule } from '@app/shared/shared.module';
import { HighlightSnippetPipe } from '@app/document/pipes/highlight-snippet.pipe';

describe('HighlightedContentComponent', () => {
    let component: HighlightedContentComponent;
    let fixture: ComponentFixture<HighlightedContentComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [SharedModule],
            declarations: [HighlightedContentComponent, HighlightSnippetPipe],
        })
            .compileComponents();

        fixture = TestBed.createComponent(HighlightedContentComponent);
        component = fixture.componentInstance;
        component.content = '';
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
