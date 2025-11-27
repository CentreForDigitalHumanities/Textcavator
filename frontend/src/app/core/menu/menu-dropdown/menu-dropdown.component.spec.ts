import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MenuDropdownComponent } from './menu-dropdown.component';
import { SharedModule } from '@shared/shared.module';

describe('MenuDropdownComponent', () => {
    let component: MenuDropdownComponent;
    let fixture: ComponentFixture<MenuDropdownComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [MenuDropdownComponent],
            imports: [SharedModule],
        })
            .compileComponents();

        fixture = TestBed.createComponent(MenuDropdownComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
