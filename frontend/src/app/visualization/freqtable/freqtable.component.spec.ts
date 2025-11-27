/* eslint-disable @typescript-eslint/naming-convention */
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import * as _ from 'lodash';
import { commonTestBed } from '@app/common-test-bed';
import { FreqtableComponent } from './freqtable.component';

describe('FreqtableComponent', () => {
    let component: FreqtableComponent;
    let fixture: ComponentFixture<FreqtableComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(FreqtableComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should convert to wide format', () => {
        component.headers = [
            {
                key: 'fruit',
                label: 'Fruit',
                isMainFactor: true,
            },
            {
                key: 'veggie',
                label: 'Veggie',
                isSecondaryFactor: true,
            },
            {
                key: 'quantity',
                label: 'Quantity',
            },
        ];
        component.wideFormatColumn = 0;

        const data = [
            {
                fruit: 'apple',
                veggie: 'carrot',
                quantity: 1,
            },
            {
                fruit: 'apple',
                veggie: 'aubergine',
                quantity: 5,
            },
            {
                fruit: 'banana',
                veggie: 'carrot',
                quantity: 3,
            },
            {
                fruit: 'banana',
                veggie: 'aubergine',
                quantity: 2,
            },
            {
                fruit: 'banana',
                veggie: 'onion',
                quantity: 4,
            },
        ];

        const factorColums = 2;
        const numericColumns = 1;
        const numberOfFruits = 2;
        const numberOfVeggies = 3;

        const [fruitHeaders, fruitData] = component.transformWideFormat(data);

        // verify shape of data
        expect(fruitHeaders.length).toBe(
            numberOfFruits * numericColumns + (factorColums - 1)
        );
        expect(fruitData.length).toBe(numberOfVeggies);

        // verify headers
        const expectedFruitHeaders = [
            {
                key: 'veggie',
                label: 'Veggie',
                isSecondaryFactor: true,
            },
            {
                key: 'quantity###apple',
                label: 'Quantity (apple)',
            },
            {
                key: 'quantity###banana',
                label: 'Quantity (banana)',
            },
        ];

        _.zip(fruitHeaders, expectedFruitHeaders).forEach(
            ([header, expected]) => {
                Object.keys(expected).forEach((property) => {
                    expect(header[property]).toBe(expected[property]);
                });
            }
        );

        // verify data
        const expectedFruitData = [
            {
                veggie: 'carrot',
                'quantity###apple': 1,
                'quantity###banana': 3,
            },
            {
                veggie: 'aubergine',
                'quantity###apple': 5,
                'quantity###banana': 2,
            },
            {
                veggie: 'onion',
                'quantity###apple': undefined,
                'quantity###banana': 4,
            },
        ];

        _.zip(fruitData, expectedFruitData).forEach(([row, expected]) => {
            Object.keys(expected).forEach((property) => {
                expect(row[property]).toBe(expected[property]);
            });
        });

        // verify shape when grouping by veggie

        component.headers = [
            {
                key: 'fruit',
                label: 'Fruit',
                isSecondaryFactor: true,
            },
            {
                key: 'veggie',
                label: 'Veggie',
                isMainFactor: true,
            },
            {
                key: 'quantity',
                label: 'Quantity',
            },
        ];
        component.wideFormatColumn = 1;

        const [veggieHeaders, veggieData] = component.transformWideFormat(data);
        expect(veggieHeaders.length).toBe(
            numberOfVeggies * numericColumns + (factorColums - 1)
        );
        expect(veggieData.length).toBe(numberOfFruits);

        // verify data

        const expectedVeggieData = [
            {
                fruit: 'apple',
                'quantity###carrot': 1,
                'quantity###aubergine': 5,
                'quantity###onion': undefined,
            },
            {
                fruit: 'banana',
                'quantity###carrot': 3,
                'quantity###aubergine': 2,
                'quantity###onion': 4,
            },
        ];

        _.zip(veggieData, expectedVeggieData).forEach(([row, expected]) => {
            Object.keys(expected).forEach((property) => {
                expect(row[property]).toBe(expected[property]);
            });
        });
    });
});
