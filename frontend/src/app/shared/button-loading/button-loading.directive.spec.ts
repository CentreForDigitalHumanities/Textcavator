import { Component, signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { ButtonLoadingDirective } from './button-loading.directive';

@Component({
    template: `
    <button class="btn btn-primary" [iaButtonLoading]="loading()">
        Test
    </button>
    `,
    imports: [CommonModule, ButtonLoadingDirective],
})
class LoadingButtonTest {
    loading = signal(false);
}

describe('iaButtonLoading', () => {
    let fixture: ComponentFixture<LoadingButtonTest>;
    let component: LoadingButtonTest;
    let button: HTMLButtonElement;

    beforeEach(() => {
        fixture = TestBed.createComponent(LoadingButtonTest);
        component = fixture.componentInstance;
        fixture.detectChanges();
        const element = fixture.debugElement.nativeElement as Element;
        button = element.querySelector('button');
    });

    it('initialises', () => {
        expect(component).toBeTruthy();
        expect(button.querySelector('.spinner-border')).toBeFalsy();
    });

    it('shows a loading spinner', () => {
        component.loading.set(true);
        fixture.detectChanges();
        expect(button.querySelector('.spinner-border')).toBeTruthy();
    });

    it('hides the loading spinner', () => {
        component.loading.set(true);
        fixture.detectChanges();
        component.loading.set(false);
        fixture.detectChanges();
        expect(button.querySelector('.spinner-border')).toBeFalsy();
    });
});
