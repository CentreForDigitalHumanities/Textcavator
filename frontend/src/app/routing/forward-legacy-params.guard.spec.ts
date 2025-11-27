import { TestBed } from '@angular/core/testing';
import { Router, RouterModule} from '@angular/router';

import { forwardLegacyParamsGuard } from './forward-legacy-params.guard';
import { Component } from '@angular/core';

@Component({
    template: '<p>Hello world!</p>',
    standalone: false
})
class TestComponent {}

describe('forwardLegacyParamsGuard', () => {
    let router: Router;
    const legacyUrl = '/search/my-corpus?query=test&compareTerm=test&compareTerm=testing&compareTerm=tester';
    const targetUrl = '/search/my-corpus?query=test&compareTerms=testing,tester';

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                RouterModule.forRoot([
                    {
                        path: 'search/:corpus',
                        component: TestComponent,
                        canActivate: [forwardLegacyParamsGuard],
                    }
                ])
            ],
            declarations: [TestComponent],
        });
        router = TestBed.inject(Router);
    });

    it('should activate valid routes', async () => {
        await router.navigateByUrl(targetUrl);
        expect(router.url).toBe(targetUrl)
    });

    it('should forward legacy parameters', async () => {
        await router.navigateByUrl(legacyUrl);
        expect(router.url).toBe(targetUrl);
    });
});
