import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { CorpusInfoComponent } from './corpus-info.component';
import { commonTestBed } from '@app/common-test-bed';

describe('CorpusInfoComponent', () => {
    let component: CorpusInfoComponent;
    let fixture: ComponentFixture<CorpusInfoComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));


    beforeEach(() => {
        fixture = TestBed.createComponent(CorpusInfoComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
