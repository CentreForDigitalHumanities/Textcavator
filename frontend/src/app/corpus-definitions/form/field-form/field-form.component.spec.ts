import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { commonTestBed } from '@app/common-test-bed';

import { FieldFormComponent } from './field-form.component';
import { CorpusDefinitionService } from '@app/corpus-definitions/corpus-definition.service';
import { SharedModule } from '@shared/shared.module';
import { ReactiveFormsModule } from '@angular/forms';
import { FormFeedbackComponent } from '../form-feedback/form-feedback.component';

describe('FieldFormComponent', () => {
    let component: FieldFormComponent;
    let fixture: ComponentFixture<FieldFormComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [
                FieldFormComponent,
                FormFeedbackComponent,
            ],
            imports: [SharedModule, ReactiveFormsModule],
            providers: [CorpusDefinitionService],
        }).compileComponents();

        fixture = TestBed.createComponent(FieldFormComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
