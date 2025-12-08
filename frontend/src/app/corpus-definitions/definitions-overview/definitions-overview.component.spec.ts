import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { DefinitionsOverviewComponent } from './definitions-overview.component';
import { commonTestBed } from '@app/common-test-bed';

describe('DefinitionsOverviewComponent', () => {
    let component: DefinitionsOverviewComponent;
    let fixture: ComponentFixture<DefinitionsOverviewComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DefinitionsOverviewComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
