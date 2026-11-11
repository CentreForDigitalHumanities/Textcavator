import { FreqTableHeader } from "@app/models";
import { transformWideFormat } from "./freqtable-utils";
import _ from "lodash";

describe('transformWideFormat', () => {
    it('converts data', () => {
        let headers: FreqTableHeader[] = [
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

        const [fruitHeaders, fruitData] = transformWideFormat(data, headers);

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

        headers = [
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

        const [veggieHeaders, veggieData] = transformWideFormat(data, headers);
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
