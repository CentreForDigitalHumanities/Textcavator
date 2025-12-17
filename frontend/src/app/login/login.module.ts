import { NgModule } from '@angular/core';
import { SharedModule } from '@shared/shared.module';
import { LoginComponent } from './login.component';
import { VerifyEmailComponent } from './verify-email/verify-email.component';
import { RequestResetComponent } from './reset-password/request-reset.component';
import { ResetPasswordComponent } from './reset-password/reset-password.component';
import { RegistrationComponent } from './registration/registration.component';
import { AboutModule } from '../about/about.module';




@NgModule({
    declarations: [
        LoginComponent,
        RegistrationComponent,
        RequestResetComponent,
        ResetPasswordComponent,
        VerifyEmailComponent,
    ],
    imports: [
        AboutModule, // to use privacy component
        SharedModule,
    ],
    exports: [
        LoginComponent,
        RegistrationComponent,
        RequestResetComponent,
        ResetPasswordComponent,
        VerifyEmailComponent,
    ]
})
export class LoginModule { }
