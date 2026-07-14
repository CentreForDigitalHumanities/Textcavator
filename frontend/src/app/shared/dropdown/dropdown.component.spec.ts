import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { Component, signal } from '@angular/core';
import { DropdownModule } from './dropdown.module';
import { CommonModule } from '@angular/common';
import { By } from '@angular/platform-browser';


@Component({
    template: `
    <ia-dropdown [value]="selected()" (onChange)="selected.set($event)">
      <span iaDropdownLabel>{{ selected()?.label || 'Select option'}}</span>
      <div iaDropdownMenu>
        @for (option of options; track option) {
          <a
            iaDropdownItem [value]="option">
            {{option.label}}
          </a>
        }
      </div>
    </ia-dropdown>
    `,
    imports: [CommonModule, DropdownModule],
})
class DropdownTestComponent {
    options = [
        { name: 'item1', label: 'Item 1' },
        { name: 'item2', label: 'Item 2' },
        { name: 'item3', label: 'Item 3' }
    ];

    selected = signal(undefined);
}

describe('DropdownComponent', () => {
    let component: DropdownTestComponent;
    let fixture: ComponentFixture<DropdownTestComponent>;

    beforeEach(() => {
        fixture = TestBed.createComponent<DropdownTestComponent>(DropdownTestComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should be created', () => {
        expect(component).toBeTruthy();
    });

    it('should render the label', async () => {
        await fixture.whenStable();

        const trigger = fixture.debugElement.query(By.css('.dropdown-trigger > button')).nativeElement;
        expect(trigger.innerHTML).toContain('Select option');

        // allow switching value
        component.selected.set(component.options[1]);
        fixture.detectChanges();
        await fixture.whenStable();

        expect(trigger.innerHTML).not.toContain('Select option');
        expect(trigger.innerHTML).toContain('Item 2');
    });

    it('should open when clicked', fakeAsync(() => {
        tick();

        const dropdown = fixture.debugElement.query(By.css('.dropdown'));

        expect(dropdown.classes['is-active']).toBeFalsy();

        const trigger = dropdown.query(By.css('.dropdown-trigger > button'));
        trigger.triggerEventHandler('click', undefined);

        tick();
        fixture.detectChanges();

        expect(dropdown.classes['is-active']).toBeTruthy();
    }));

});
