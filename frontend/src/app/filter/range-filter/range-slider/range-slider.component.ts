import { Component, computed, effect, ElementRef, input, output, signal, viewChild, WritableSignal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import _ from 'lodash';
import { asyncScheduler, filter, fromEvent, OperatorFunction, Subject, switchMap, takeUntil, throttleTime } from 'rxjs';

const filterLeftClick: OperatorFunction<MouseEvent, MouseEvent> = filter((event) =>
    event.button === 0
);

const listenToMouseMove: OperatorFunction<any, MouseEvent> = switchMap(() =>
    fromEvent<MouseEvent>(document, 'mousemove').pipe(
        takeUntil(fromEvent(document, 'mouseup')),
        throttleTime(100, asyncScheduler, { leading: true, trailing: true}),
    )
);


@Component({
    selector: 'ia-range-slider',
    imports: [],
    templateUrl: './range-slider.component.html',
    styleUrl: './range-slider.component.scss',
})
export class RangeSliderComponent {
    /** Minimum possible value */
    min = input.required<number>();
    /** Maximum possible value */
    max = input.required<number>();
    /** Step size */
    step = input<number>(1);
    /** Input to override the component's internal value */
    value = input<[number, number]>();
    ariaLabel = input.required<string>();
    onChange = output<[number, number]>();

    // Lower/upper range values. Initial value is set based on min/max/value inputs.
    lower = signal<number>(-Infinity);
    upper = signal<number>(Infinity);

    // Helper signals to calculate element positions
    lowerPosition = computed(() => this.thumbPosition(this.lower(), this.min(), this.max()));
    upperPosition = computed(() => this.thumbPosition(this.upper(), this.min(), this.max()));
    rangePosition = computed(() => this.getRangePosition(this.lower(), this.min(), this.max()));
    rangeWidth = computed(() => this.getRangeWidth(this.lower(), this.upper(), this.min(), this.max()));

    // Click events for the lower/upper handles.
    lowerClick$ = new Subject<MouseEvent>();
    upperClick$ = new Subject<MouseEvent>();

    slider = viewChild.required<ElementRef<HTMLElement>>('slider');

    constructor() {
        // Input/output handling
        effect(() => this.lower.update((value) =>
            _.clamp(value, this.min(), this.max())
        ));
        effect(() => this.upper.update((value) =>
            _.clamp(value, this.min(), this.max())
        ));
        effect(() => {
            if (this.value()) {
                this.lower.set(this.value()[0]);
                this.upper.set(this.value()[1]);
            }
        });
        effect(() =>
            this.onChange.emit([this.lower(), this.upper()])
        );

        // Mouse drag handling
        this.lowerClick$.pipe(
            filterLeftClick,
            listenToMouseMove,
            takeUntilDestroyed(),
        ).subscribe((event) =>
            this.onThumbDrag(event, this.lower, this.min(), this.upper()),
        );
        this.upperClick$.pipe(
            filterLeftClick,
            listenToMouseMove,
            takeUntilDestroyed(),
        ).subscribe((event) =>
            this.onThumbDrag(event, this.upper, this.lower(), this.max()),
        );
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

    private onThumbDrag(event: MouseEvent, signal: WritableSignal<number>, min: number, max: number) {
        const slider = this.slider().nativeElement;
        const left = slider.offsetLeft;
        const right = slider.offsetLeft + slider.offsetWidth;
        const ratio = (event.pageX - left) / (right - left);
        const value = this.min() + (this.max() - this.min()) * ratio;
        const validated = _.clamp(this.round(value), min, max);
        signal.set(validated);
    }

    /** Round value to nearest multiple of step size */
    private round(value: number): number {
        const step = this.step();
        return Math.round(value / step) * step;
    }

    private thumbPosition(value: number, min: number, max: number): string {
        const ratio = (value - min) / (max - min);
        return `calc(${100 * ratio}% - 0.5em)`;
    }

    private getRangePosition(lower: number, min: number, max: number): string {
        const ratio = (lower - min) / (max - min);
        return `${100 * ratio}%`;
    }

    private getRangeWidth(lower: number, upper: number, min: number, max: number) {
        const ratio = (upper - lower) / (max - min);
        return `${100 * ratio}%`;
    }
}
