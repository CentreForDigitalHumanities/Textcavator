import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SliderComponent } from './slider.component';

describe('SliderComponent', () => {
    let component: SliderComponent;
    let fixture: ComponentFixture<SliderComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [SliderComponent]
        })
            .compileComponents();

        fixture = TestBed.createComponent(SliderComponent);
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
