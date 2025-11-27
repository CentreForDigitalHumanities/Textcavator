import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { TabsComponent } from './tabs.component';
import { commonTestBed } from '@app/common-test-bed';

describe('TabsComponent', () => {
    let component: TabsComponent;
    let fixture: ComponentFixture<TabsComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(TabsComponent);
        component = fixture.componentInstance;
        component.tabs = [{
            label: 'First tab',
            elementId: 'tab-1',
            id: 1
        }, {
            label: 'Second tab',
            elementId: 'tab-2',
            id: 2
        }];
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should produce slug tab IDs', () => {
        const tabIdNumerical = 1;
        const tabIdString = 'General Information';
        expect(component.tabLinkId(tabIdNumerical)).toEqual('tab-1');
        expect(component.tabLinkId(tabIdString)).toEqual(
            'tab-general-information'
        );
    });
});
