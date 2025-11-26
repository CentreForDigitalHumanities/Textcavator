import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { commonTestBed } from '@app/common-test-bed';

import { TimelineComponent } from './timeline.component';
import { QueryModel } from '@models';
import { corpusFactory } from 'mock-data/corpus';

describe('TimelineComponent', () => {
    let component: TimelineComponent;
    let fixture: ComponentFixture<TimelineComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(TimelineComponent);
        component = fixture.componentInstance;
        component.queryModel = new QueryModel(corpusFactory());
        component.visualizedField = component.queryModel.corpus.fields[2];
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should calculate correct time categories', () => {
        expect(component.calculateTimeCategory(new Date('1950-01-01'), new Date('1950-01-05'))).toEqual('day');
        expect(component.calculateTimeCategory(new Date('1950-01-01'), new Date('1950-02-01'))).toEqual('week');
        expect(component.calculateTimeCategory(new Date('1950-01-01'), new Date('1950-06-01'))).toEqual('month');
        expect(component.calculateTimeCategory(new Date('1950-01-01'), new Date('1951-01-01'))).toEqual('year');
    })

    it('should calibrate the x axis with a margin', () => {
        component.setTimeDomain();
        const min = new Date('1802-01-01');
        const max = new Date('1804-01-01');
        expect(component.callibratexAxis(min, -1)).toEqual(new Date('1801-01-01'));
        expect(component.callibratexAxis(max)).toEqual(new Date('1805-01-01'));
    })
});
