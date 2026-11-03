import { Component, computed, effect, input, signal, WritableSignal } from '@angular/core';
import _ from 'lodash';

@Component({
    selector: 'ia-slider',
    imports: [],
    templateUrl: './slider.component.html',
    styleUrl: './slider.component.scss',
})
export class SliderComponent {
    min = input.required<number>();
    max = input.required<number>();
    step = input<number>(1);

    lower = signal<number>(NaN);
    upper = signal<number>(NaN);

    lowerPosition = computed(() => this.valueToPosition(this.lower(), this.min(), this.max()));
    upperPosition = computed(() => this.valueToPosition(this.upper(), this.min(), this.max()));

    constructor() {
        effect(() => this.lower.set(this.min()));
        effect(() => this.upper.set(this.max()));
    }

    increase(signal: WritableSignal<number>, min: number, max: number) {
        signal.update((value) =>
            _.clamp(value + this.step(), min, max)
        );
    }

    decrease(signal: WritableSignal<number>, min: number, max: number) {
        signal.update((value) =>
            _.clamp(value - this.step(), min, max)
        );
    }

    valueToPosition(value: number, min: number, max: number): string {
        const ratio = (value - min) / (max - min);
        return `${100 * ratio}%`;
    }
}
