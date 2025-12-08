import { modulo } from './utils';

export const PALETTES = [
    ['#3F51B5', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499', '#DDDDDD'],
    // colour-blind friendly colorPalette retrieved from colorbrewer2.org
    ['#a6611a', '#dfc27d', '#80cdc1', '#018571', '#543005', '#bf812d', '#f6e8c3', '#c7eae5', '#35978f', '#003c30'],
    // d3 category10 palette
    ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf' ],
    // greyscale - occasionally useful for printing
    ['#000', '#bbb', '#444']
];

export const selectColor = (palette?: string[], index?: number): string => {
    if (palette) {
        const i = index || 0;
        return palette[modulo(i, palette.length)];
    } else {
        return '#3F51B5'; // textcavator primary
    }
};
