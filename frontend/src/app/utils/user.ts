import * as _ from 'lodash';
import { User, UserResponse } from '@models';

/* Transforms backend user response to User object
*
* @param result User response data
* @returns User object
*/
export const parseUserData = (result: UserResponse): User => new User(
    result.id,
    result.name,
    result.is_admin,
    result.download_limit == null ? 0 : result.download_limit,
    result.saml,
    result.profile.enable_search_history,
    result.profile.can_edit_corpora,
);

/**
 * Transfroms User data to backend UserResponse object
 *
 * Because this is used for patching, the data can be partial
 *
 * @param data (partial) User object
 * @returns UserResponse object
 */
export const encodeUserData = (data: Partial<User>): Partial<UserResponse> => {
    const changeKeys = {
        name: 'username',
        isAdmin: 'is_admin',
        downloadLimit: 'download_limit',
        isSamlLogin: 'saml',
        enableSearchHistory: 'profile.enable_search_history',
        canEditCorpora: 'profile.can_edit_corpora',
    };

    const encoded = {};

    _.keys(data).forEach(key => {
        const value = data[key];
        const path = changeKeys[key] ? _.toPath(changeKeys[key]) : key;
        _.set(encoded, path, value);
    });

    return encoded;
};
