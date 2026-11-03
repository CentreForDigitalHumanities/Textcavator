import { Component, computed, effect, ElementRef, input, signal, viewChild, WritableSignal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import _ from 'lodash';
import { fromEvent, Subject, switchMap, takeUntil, throttleTime } from 'rxjs';

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

    lower = signal<number>(-Infinity);
    upper = signal<number>(Infinity);

    lowerPosition = computed(() => this.valueToPosition(this.lower(), this.min(), this.max()));
    upperPosition = computed(() => this.valueToPosition(this.upper(), this.min(), this.max()));

    lowerClick$ = new Subject<void>();
    lowerDrag$ = this.lowerClick$.pipe(
        switchMap(() => fromEvent<MouseEvent>(document, 'mousemove').pipe(
            takeUntil(fromEvent(document, 'mouseup')),
            throttleTime(100),
        )),
    );

    slider = viewChild.required<ElementRef<HTMLElement>>('slider');

    constructor() {
        effect(() => this.lower.update((value) =>
            _.clamp(value, this.min(), this.max())
        ));
        effect(() => this.upper.update((value) =>
            _.clamp(value, this.min(), this.max())
        ));

        this.lowerDrag$.pipe(
            takeUntilDestroyed(),
        ).subscribe((event) =>
            this.onThumbDrag(event, this.lower, this.min(), this.upper()),
        )
    }

    onThumbDrag(event: MouseEvent, signal: WritableSignal<number>, min: number, max: number) {
        const slider = this.slider().nativeElement;
        const left = slider.offsetLeft;
        const right = slider.offsetLeft + slider.offsetWidth;
        const ratio = (event.pageX - left) / (right - left);
        const value = this.min() + (this.max() - this.min()) * ratio;
        const clamped = _.clamp(value, min, max);
        signal.set(clamped);
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
        return `calc(${100 * ratio}% - 0.5em)`;
    }
}
