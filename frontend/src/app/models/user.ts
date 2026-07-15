import * as _ from 'lodash';

interface UserProfileResponse {
    enable_search_history: boolean;
    can_edit_corpora: boolean;
}

export interface UserResponse {
    id: number;
    name: string;
    username?: string;
    email: string;
    download_limit: number;
    is_admin: boolean;
    saml: boolean;
    profile: UserProfileResponse;
}

export class User {
    constructor(
        public id,
        public name: string,
        public isAdmin: boolean,
        public downloadLimit: number = 0, // The download limit for this user, will be 0 if there is no limit.
        public isSamlLogin: boolean,
        public enableSearchHistory: boolean,
        public canEditCorpora: boolean,
    ) {}
}
