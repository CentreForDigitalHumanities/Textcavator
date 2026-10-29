/* eslint-disable @typescript-eslint/naming-convention */
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import * as _ from 'lodash';
import { commonTestBed } from '@app/common-test-bed';
import { FreqtableComponent } from './freqtable.component';

describe('FreqtableComponent', () => {
    let component: FreqtableComponent;
    let fixture: ComponentFixture<FreqtableComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(FreqtableComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

});
