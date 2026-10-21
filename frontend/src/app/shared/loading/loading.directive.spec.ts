import { Component, signal } from '@angular/core';
import { LoadingDirective } from './loading.directive';
import { CommonModule } from '@angular/common';
import { ComponentFixture, TestBed } from '@angular/core/testing';

@Component({
    imports: [CommonModule, LoadingDirective],
    template: `
<div [iaLoading]="loading()">
    <p>Hello, world!<p>
</div>
    `
})
class LoadingDirectiveTest {
    loading = signal(true);
}

describe('LoadingDirective', () => {
    let fixture: ComponentFixture<LoadingDirectiveTest>;
    let component: LoadingDirectiveTest;

    beforeEach(() => {
        fixture = TestBed.createComponent(LoadingDirectiveTest);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create an instance', () => {
        expect(component).toBeTruthy();
    });

    it('shows a loading spinner', () => {
        const el = (fixture.nativeElement as HTMLElement);
        expect(el.querySelector('.spinner-border')).toBeTruthy();
    });

    it('hides the loading spinner', () => {
        component.loading.set(false);
        fixture.detectChanges();
        const el = (fixture.nativeElement as HTMLElement);
        expect(el.querySelector('.spinner-border')).toBeFalsy();
    });
});
