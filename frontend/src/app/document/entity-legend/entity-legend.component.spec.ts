import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EntityLegendComponent } from './entity-legend.component';
import { SharedModule } from '@app/shared/shared.module';


describe('EntityLegendComponent', () => {
    let component: EntityLegendComponent;
    let fixture: ComponentFixture<EntityLegendComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [EntityLegendComponent],
            imports: [SharedModule],
        })
            .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(EntityLegendComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
