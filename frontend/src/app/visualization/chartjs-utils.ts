
import { Defaults } from 'chart.js';

export const setThemefaults = (defaults: Defaults) => {
    const style = window.getComputedStyle(document.body);

    defaults.color = style.getPropertyValue('--bulma-text-strong');
    defaults.borderColor = style.getPropertyValue('--bulma-border');
}
