import {
    ActivatedRouteSnapshot, CanActivateFn, createUrlTreeFromSnapshot, Params,
    RouterStateSnapshot
} from '@angular/router';
import * as _ from 'lodash';
import { COMPARE_TERMS_KEY, DELIMITER } from '../models/compared-queries';

const LEGACY_COMPARE_TERMS_PARAM = 'compareTerm';

/**
 * Forwards URLs that include outdated query parameters.
 *
 * This forwards URLs with the outdated `compareTerm` parameter. (May be expanded with
 * other parameters in the future.) Allows old links/bookmarks to keep functioning.
 *
 * For example:
 * `?query=a&compareTerm=a&compareTerm=b&compareTerm=c`
 * will be redirected to
 * `?query=a&compareTerms=b,c`
 */
export const forwardLegacyParamsGuard: CanActivateFn = (
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
) => {
    if (hasLegacyParams(route)) {
        const url = createUrlTreeFromSnapshot(route, ['.']);
        // include updated query parameters
        url.queryParams = updatedCompareTermsParams(route);
        // preserve fragment
        url.fragment = route.fragment;
        return url;
    }
    return true;
};

const hasLegacyParams = (route: ActivatedRouteSnapshot): boolean => {
    return route.queryParamMap.has(LEGACY_COMPARE_TERMS_PARAM);
}

/**
 * Returns updated version of the query parameters in a URL.
 *
 * Replaces legacy `compareTerm` with `compareTerms` parameter. Returns the Params object
 * with updated values.
 */
const updatedCompareTermsParams = (route: ActivatedRouteSnapshot): Params => {
    const comparedTerms = legacyComparedTerms(route);
    const params = _.omit(route.queryParams, [LEGACY_COMPARE_TERMS_PARAM]);
    params[COMPARE_TERMS_KEY] = comparedTerms.join(DELIMITER);
    return params;
}

/** The compared terms in a URL in legacy format
 *
 * Example of legacy parameters: `?query=a&compareTerm=a&compareTerm=b&compareTerm=c`
 *
 * This would return `['b', 'c']` as the compared terms.
 */
const legacyComparedTerms = (route: ActivatedRouteSnapshot): string[] => {
    const query = route.queryParamMap.get('query');
    const allTerms = route.queryParamMap.getAll(LEGACY_COMPARE_TERMS_PARAM);
    return _.without(allTerms, query);
}
