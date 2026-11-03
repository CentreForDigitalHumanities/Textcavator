import { Component, effect, input, signal, WritableSignal } from '@angular/core';
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

    constructor() {
        effect(() => this.lower.set(this.min()));
        effect(() => this.upper.set(this.max()));
    }

    onThumbKeydown(event: KeyboardEvent, signal: WritableSignal<number>) {
        if (event.key == 'ArrowRight') {
            this.increase(signal);
        }
        if (event.key == 'ArrowLeft') {
            this.decrease(signal);
        }
    }

    increase(signal: WritableSignal<number>) {
        signal.update((value) =>
            this.clampValue(value + this.step())
        );
    }

    decrease(signal: WritableSignal<number>) {
        signal.update((value) =>
            this.clampValue(value - this.step())
        );
    }

    private clampValue(value: number): number {
        return _.clamp(value, this.min(), this.max())
    }
}
