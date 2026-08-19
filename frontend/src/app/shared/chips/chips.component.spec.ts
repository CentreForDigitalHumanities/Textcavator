import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChipsComponent } from './chips.component';

describe('ChipsComponent', () => {
    let component: ChipsComponent;
    let fixture: ComponentFixture<ChipsComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ChipsComponent]
        })
            .compileComponents();

        fixture = TestBed.createComponent(ChipsComponent);
        component = fixture.componentInstance;
        fixture.componentRef.setInput('itemName', 'thingamajig');
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
