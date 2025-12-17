import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { CreateDefinitionComponent } from './create-definition.component';
import { commonTestBed } from '@app/common-test-bed';

describe('CreateDefinitionComponent', () => {
    let component: CreateDefinitionComponent;
    let fixture: ComponentFixture<CreateDefinitionComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(CreateDefinitionComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
