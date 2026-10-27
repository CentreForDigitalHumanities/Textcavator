import { BehaviorSubject } from 'rxjs';

interface HasName {
    name: string;
}

/**
 * Find an item by its `name` property.
 *
 * @param items an array of items that have a `name` property
 * @param name the name of the item you want to find
 * @returns Tthe first item that matches the given name. Returns the first match or `undefined` if nothing matches.
 */
export const findByName = <T extends HasName>(items: T[], name: string): T =>
    items.find(item => item.name === name);

/**
 * mark a loading indicator while waiting for a promise
 *
 * @param isLoading a BehaviorSubject that should be set to `true` while waiting
 * @param promise a promise
 * @returns a promise for the result of `promise`, but `isLoading` will be updated appropriately.
 */
export const showLoading = <T>(isLoading: BehaviorSubject<boolean>, promise: Promise<T>): Promise<T> => {
    isLoading.next(true);
    return promise.then(result => {
        isLoading.next(false);
        return result;
    });
};

export const modulo = (n: number, d: number): number => ((n % d) + d) % d;

/**
 * Pad a number with leading zeros to a given length and return it as a string.
 */
export function padWithZero(value: number, length: number): string {
    return value.toString().padStart(length, '0');
}
