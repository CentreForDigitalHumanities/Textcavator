# Styling

This document covers CSS styling for the frontend.

Textcavator uses the CSS framework [bulma](https://bulma.io/documentation/).

Initial and derived variables from bulma are customised in [_utilities.css](/frontend/src/_utilities.scss). This file only defines variables and mixins and can be imported in component stylesheets. [styles.csss](/frontend/src/styles.scss) includes site-wide selectors.

## Dark mode

Dark mode is managed by the [ThemeService](/frontend/src/app/services/theme.service.ts).

The service sets `data-theme="dark"` / `data-theme="light"` on the HTML root node, which is used by CSS selectors. If you need to observe the theme in a component, you can also use `ThemeService.theme$`.

## Other libraries

Several other libraries are used to provide components, visualisations, etc. These are often customised to fit the site theme and/or adapt to dark mode.

## PrimeNG components

We use several components from [primeNG](https://v19.primeng.org/). [primeng-theme.ts](/frontend/src/app/primeng-theme.ts) defines the preset to customise primeNG styles, mostly using bulma CSS variables.

## Chart.js

[select-color.ts](/frontend/src/app/utils/select-color.ts) defines the colour palettes for data visualisations and a utility function to select the nth colour. There are several palettes; the default is chosen to fit the site theme. The [palette selector](/frontend/src/app/visualization/visualization-footer/palette-select/palette-select.component.ts) lets users choose a preferred palette; the `VisualizationComponent` and `WordModelsComponent` provide the chosen palette as input to visualisation components.

Chart.js has no built-in "dark mode". The `ThemeService` adjusts several defaults to get readable charts in dark mode, and updates all chart instances when the theme changes.

## Vega

To let a Vega visualisation adapt to dark/light mode, relevant colours should depend on a signal.

Add the following signal in your vega document:

```json
{
    "name": "theme",
    "description": "Current site theme (light/dark)",
    "bind": { "element": "#current-theme" }
}
```

The value of the `theme` signal will be `"dark"` or `"light"`. When you define colours in your document, let theme depend on this signal, e.g. with a mark like this:

```json
{
    "marks": [
        {
            "type": "text",
            // ...
            "encode": {
                "update": {
                    "fill": {"signal": "theme === \"dark\" ? \"white\" : \"black\""}
                },
            }
        },
    ]
}
```

When you display the visualisation, include a [theme indicator](/frontend/src/app/visualization/theme-indicator.directive.ts) on your page like this:

```html
<input iaThemeIndicator >
```

The Vega graph will bind the `theme` signal to the value of this element. The element will not be visible to users.
