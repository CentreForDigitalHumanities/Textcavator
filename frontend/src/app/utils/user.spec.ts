import * as _ from 'lodash';
import { User, UserResponse } from '@models';
import { parseUserData, encodeUserData } from './user';

/**
 * check if an object is a partial version of another object
 *
 * Verify that each key in `part` has the same value in `whole`,
 * but ignore any properties of `whole` that are ommitted in `part`.
 */
const isPartialOf = <T>(part: Partial<T>, whole: T): boolean => {
    const picked = _.pick(whole, _.keys(part));
    return _.isEqual(part, picked);
};

const customMatchers = {
    /** expect an object to be a partial version of another object */
    toBePartialOf: (matchersUtil) => ({
        compare: <T>(actual: Partial<T>, expected: T) => {
            const pass = isPartialOf(actual, expected);
            return { pass };
        }
    })
};

describe('user API conversion', () => {
    let user: User;
    let userResponse: UserResponse;

    beforeEach(() => {
        jasmine.addMatchers(customMatchers);
    });

    beforeEach(() => {
        user = new User(
            1,
            'Hamlet',
            false,
            10000,
            false,
            true,
            false,
        );
    });

    beforeEach(() => {
        userResponse = {
            id: 1,
            name: 'Hamlet',
            username: 'Hamlet',
            email: 'hamlet@elsinore.dk',
            download_limit: 10000,
            is_admin: false,
            saml: false,
            profile: {
                enable_search_history: true,
                can_edit_corpora: false,
            }
        };
    });

    it('should convert a user response to a user object', () => {
        expect(parseUserData(userResponse)).toEqual(user);
    });

    it('should convert a user to a user response object', () => {
        const encoded = encodeUserData(user);
        (expect(encoded) as any).toBePartialOf(userResponse);
    });

    it('should define inverse functions', () => {
        // results have to to be merged with the API data because User does not contain
        // all API properties

        const encoded = encodeUserData(user);
        const decoded = parseUserData(Object.assign(userResponse, encoded));
        expect(decoded).toEqual(user);

        const parsed = parseUserData(userResponse);
        const unparsed = encodeUserData(parsed);
        expect(Object.assign(userResponse, unparsed)).toEqual(userResponse);
    });
});
