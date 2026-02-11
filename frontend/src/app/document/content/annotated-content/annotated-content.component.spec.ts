import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AnnotatedContentComponent } from './annotated-content.component';
import { AnnotationSegmentsPipe } from '@app/document/pipes/annotation-segments.pipe';
import { SharedModule } from 'primeng/api';

describe('AnnotatedContentComponent', () => {
    let component: AnnotatedContentComponent;
    let fixture: ComponentFixture<AnnotatedContentComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [AnnotatedContentComponent, AnnotationSegmentsPipe],
            imports: [SharedModule],
        })
            .compileComponents();

        fixture = TestBed.createComponent(AnnotatedContentComponent);
        component = fixture.componentInstance;
        component.content = '';
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
