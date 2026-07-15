import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BackToTopButton } from './back-to-top-button.component';

describe('BackToTopButtonComponent', () => {
    let component: BackToTopButton;
    let fixture: ComponentFixture<BackToTopButton>;

    beforeEach(async () => {
        fixture = TestBed.createComponent(BackToTopButton);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
