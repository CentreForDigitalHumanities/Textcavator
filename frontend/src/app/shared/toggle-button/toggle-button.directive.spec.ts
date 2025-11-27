import { Component } from '@angular/core';
import { ToggleButtonDirective } from './toggle-button.directive';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommonModule } from '@angular/common';

@Component({
    template: `
    <button class="button" iaToggleButton [active]="active" [activeClass]="class">
        Test
    </button>
    `,
    standalone: false
})
class ToggleButtonTestComponent {
    active = false;
    class = 'is-primary';
}

describe('ToggleButtonDirective', () => {
    let fixture: ComponentFixture<ToggleButtonTestComponent>;
    let component: ToggleButtonTestComponent;
    let button: HTMLButtonElement;

    beforeEach(() => {
        TestBed.configureTestingModule({
            declarations: [ToggleButtonTestComponent, ToggleButtonDirective],
            imports: [CommonModule],
        });
        fixture = TestBed.createComponent(ToggleButtonTestComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
        const element = fixture.debugElement.nativeElement as Element;
        button = element.querySelector('button');

    });

    it('should show toggle state', () => {
        expect(button.className).toEqual('button');
        expect(button.getAttribute('aria-pressed')).toBe('false');

        component.active = true;
        fixture.detectChanges();

        expect(button.className).toEqual('button is-primary');
        expect(button.getAttribute('aria-pressed')).toBe('true');
    });

    it('should set the CSS class through input', () => {
        component.class = 'is-danger';
        component.active = true;
        fixture.detectChanges();

        expect(button.className).toEqual('button is-danger');
    });
});
