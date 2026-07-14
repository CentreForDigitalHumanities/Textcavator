import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BackToTopButton } from './back-to-top-button.component';
import { CommonModule } from '@angular/common';

describe('BackToTopButtonComponent', () => {
    let component: BackToTopButton;
    let fixture: ComponentFixture<BackToTopButton>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [BackToTopButton],
            imports: [CommonModule]
        })
            .compileComponents();

        fixture = TestBed.createComponent(BackToTopButton);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
