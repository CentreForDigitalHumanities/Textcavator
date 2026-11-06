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
        fixture.componentRef.setInput('default', new Date(2020, 1, 1));
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('converts dates to strings correctly', () => {
        const inputs = [
            new Date(2020, 1, 1),
            new Date(2020, 11, 31),
            new Date(2020, 0, 1),
        ];
        const expectedOutputs = [
            '2020-02-01',
            '2020-12-31',
            '2020-01-01',
        ];

        inputs.forEach((input, index) => {
            const output = component['date2String'](input);
            expect(output).toEqual(expectedOutputs[index]);
        });
    })
});
