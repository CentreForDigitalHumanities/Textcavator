import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RangeSliderComponent } from './range-slider.component';

describe('RangeSliderComponent', () => {
    let component: RangeSliderComponent;
    let fixture: ComponentFixture<RangeSliderComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [RangeSliderComponent]
        })
            .compileComponents();

        fixture = TestBed.createComponent(RangeSliderComponent);
        fixture.componentRef.setInput('min', 0);
        fixture.componentRef.setInput('max', 1000);
        fixture.componentRef.setInput('ariaLabel', 'Test');
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
