import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { DatePickerComponent } from './date-picker.component';
import { commonTestBed } from '@app/common-test-bed';
import { NgbDateParserFormatter } from '@ng-bootstrap/ng-bootstrap/datepicker';

describe('DatePickerComponent', () => {
    let component: DatePickerComponent;
    let fixture: ComponentFixture<DatePickerComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));


    beforeEach(() => {
        fixture = TestBed.createComponent(DatePickerComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should reject invalid manually entered dates', () => {
        const formatter = fixture.debugElement.injector.get(NgbDateParserFormatter);

        expect(formatter.parse('xx-12-2020')).toBeNull();
        expect(formatter.parse('31-02-2020')).toBeNull();
    });

    it('should parse valid manually entered dates', () => {
        const formatter = fixture.debugElement.injector.get(NgbDateParserFormatter);

        expect(formatter.parse('29-02-2020')).toEqual({
            day: 29,
            month: 2,
            year: 2020,
        });
        expect(formatter.parse('1-2-2020')).toEqual({
            day: 1,
            month: 2,
            year: 2020,
        });
    });
});
