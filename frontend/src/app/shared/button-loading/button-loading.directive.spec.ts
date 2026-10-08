import { Component, signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { ButtonLoadingDirective } from './button-loading.directive';

@Component({
    template: `
    <button class="btn btn-primary" [iaButtonLoading]="loading()" (click)="handleClick()">
        Test
    </button>
    `,
    imports: [CommonModule, ButtonLoadingDirective],
})
class LoadingButtonTest {
    loading = signal(false);

    handleClick() {}
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

    it('forwards click events', () => {
        const spy = spyOn(component, 'handleClick');
        expect(spy).not.toHaveBeenCalled()
        button.click();
        expect(spy).toHaveBeenCalled();
    });

    it('blocks click events while loading', () => {
        component.loading.set(true);
        fixture.detectChanges();
        const spy = spyOn(component, 'handleClick');
        button.click();
        expect(spy).not.toHaveBeenCalled();
    });
});

@Component({
    template: `
    <form (submit)="handleSubmit($event)">
        <label>Test</label>
        <input type="text">
        <button class="btn btn-primary" type="submit" [iaButtonLoading]="loading()" >
            Submit
        </button>
    </form>
    `,
    imports: [CommonModule, ButtonLoadingDirective],
})
class LoadingButtonFormTest {
    loading = signal(false);

    handleSubmit(event) {
        event.preventDefault();
    }
}

describe('iaButtonLoading', () => {
    let fixture: ComponentFixture<LoadingButtonFormTest>;
    let component: LoadingButtonFormTest;
    let button: HTMLButtonElement;

    beforeEach(() => {
        fixture = TestBed.createComponent(LoadingButtonFormTest);
        component = fixture.componentInstance;
        fixture.detectChanges();
        const element = fixture.debugElement.nativeElement as Element;
        button = element.querySelector('button');
    });

    it('forwards default events', () => {
        const spy = spyOn(component, 'handleSubmit').and.callThrough();
        expect(spy).not.toHaveBeenCalled()
        button.click();
        expect(spy).toHaveBeenCalled();
    });

    it('prevents default events while loading', () => {
        component.loading.set(true);
        fixture.detectChanges();
        const spy = spyOn(component, 'handleSubmit').and.callThrough();
        button.click();
        expect(spy).not.toHaveBeenCalled();
    });
});
