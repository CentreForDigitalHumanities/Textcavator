import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { commonTestBed } from '@app/common-test-bed';

import { VisualizationComponent } from './visualization.component';

describe('VisualizationComponent', () => {
    let component: VisualizationComponent;
    let fixture: ComponentFixture<VisualizationComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(VisualizationComponent);
        component = fixture.componentInstance;
        component.corpus = {
            fields: [
                {
                    displayName: 'Test Field',
                    name: 'test_field',
                },
            ],
        } as any;
        fixture.detectChanges();
    });

    it('should be created', () => {
        expect(component).toBeTruthy();
    });

    afterAll(() => {
        fixture.destroy();
    });
});
