import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { VisualizationFooterComponent } from './visualization-footer.component';

describe('VisualizationFooterComponent', () => {
    let component: VisualizationFooterComponent;
    let fixture: ComponentFixture<VisualizationFooterComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));


    beforeEach(() => {
        fixture = TestBed.createComponent(VisualizationFooterComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
