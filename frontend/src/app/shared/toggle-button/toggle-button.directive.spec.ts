import { Component, signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { ToggleButtonDirective } from './toggle-button.directive';

@Component({
    template: `
    <button class="btn btn-body" iaToggleButton [active]="active()" [activeClass]="class()">
        Test
    </button>
    `,
    imports: [CommonModule, ToggleButtonDirective],
})
class ToggleButtonTestComponent {
    active = signal(false);
    class = signal('btn-primary');
}

describe('ToggleButtonDirective', () => {
    let fixture: ComponentFixture<ToggleButtonTestComponent>;
    let component: ToggleButtonTestComponent;
    let button: HTMLButtonElement;

    beforeEach(() => {

        fixture = TestBed.createComponent(ToggleButtonTestComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
        const element = fixture.debugElement.nativeElement as Element;
        button = element.querySelector('button');

    });

    it('should show toggle state', () => {
        expect(button.className).toEqual('btn btn-body');
        expect(button.getAttribute('aria-pressed')).toBe('false');

        component.active.set(true);
        fixture.detectChanges();

        expect(button.className).toEqual('btn btn-primary');
        expect(button.getAttribute('aria-pressed')).toBe('true');
    });

    it('should set the CSS class through input', () => {
        component.class.set('btn-danger');
        component.active.set(true)
        fixture.detectChanges();

        expect(button.className).toEqual('btn btn-danger');
    });
});
