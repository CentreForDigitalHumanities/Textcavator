import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { SimilarityChartComponent } from './similarity-chart.component';


const EXAMPLE_DATA = {
    labels: ['1900-1910', '1910-1920', '1920-1930'],
    datasets: [
        {
            label: 'test',
            data: [0.2, 0.3, 0.1],
        },
        {
            label: 'test2',
            data: [0.2, 0.4, 0.1]
        },
        {
            label: 'test3',
            data: [0.1, 0.5, 0.6]
        }
    ]
};


describe('SimilarityChartComponent', () => {
    let component: SimilarityChartComponent;
    let fixture: ComponentFixture<SimilarityChartComponent>;


    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));


    beforeEach(() => {
        fixture = TestBed.createComponent(SimilarityChartComponent);
        component = fixture.componentInstance;
        component.timeIntervals = EXAMPLE_DATA.labels;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

});
