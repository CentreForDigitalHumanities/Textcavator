import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { DeleteSearchHistoryComponent } from './delete-search-history.component';
import { commonTestBed } from '@app/common-test-bed';

describe('DeleteSearchHistoryComponent', () => {
    let component: DeleteSearchHistoryComponent;
    let fixture: ComponentFixture<DeleteSearchHistoryComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DeleteSearchHistoryComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
