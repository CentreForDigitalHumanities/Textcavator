import { Component, Input } from '@angular/core';

@Component({
    selector: 'ia-form-feedback',
    templateUrl: './form-feedback.component.html',
    styleUrl: './form-feedback.component.scss',
    standalone: false,
})
export class FormFeedbackComponent {
    @Input() showSuccess: boolean;
    @Input() showError: boolean;
    @Input() showInvalid: boolean;
}
