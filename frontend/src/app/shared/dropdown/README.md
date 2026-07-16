# Dropdown component

The dropdown component is a wrapper around the [ng-bootstrap dropdown](https://ng-bootstrap.github.io/#/components/dropdown/examples).

Bootstrap dropdowns are generic - this component is more specific for a single-select listbox. Additions to the bootstrap dropdown:
- Assigns a [combobox](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/combobox_role) / [listbox](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/listbox_role) role to the elements (and some related ARIA properties).
- Handles the data logic for single-select. You can listen to the selected value with `(onChange)` or by binding a `FormControl`.

Typical usage looks like this:

```html
<label id="lucky-number-label">Lucky number</label>
<ia-dropdown (onChange)="selection = $event" labelledBy="lucky-number-label">
    <span iaDropdownLabel>{{selection}}</span>
    <div iaDropdownMenu>
        <button iaDropdownItem [value]="3">
            3
        </button>
        <button iaDropdownItem [value]="5">
            5
        </button>
    </div>
</ia-dropdown>
```

See [bootstrap documentation](https://getbootstrap.com/docs/5.3/components/dropdowns/) for more information on layout.

## API

Dropdown items support:

- `[value]` input: the value that the item represents.
- `(onSelect)` output: emits the _value_ of the item when it is selected through user interaction (e.g. by clicking it).

The dropdown component supports:

- `[value]` input: this sets the selected value in the menu - use this to set the value from the parent component.
- `[disabled]` input: if `true`, this disables the entire menu.
- `[labelledBy]` input: sets the ID of the element labelling the dropdown. This is required to make the dropdown accessible.
- `[triggerClass]`: additional CSS classes for the trigger button
- `(onChanges)` output: emits all changes to the selected value, including when it is set through input. If you only want to listen to UI events, use `(onSelect)` on the individual items instead.
- `[formControl]`: register a control in a [reactive form](https://angular.dev/guide/forms/reactive-forms).

