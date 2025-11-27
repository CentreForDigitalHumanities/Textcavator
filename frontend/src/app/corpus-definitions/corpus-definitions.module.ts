import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { SharedModule } from '@shared/shared.module';
import { QuillModule } from 'ngx-quill';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';
import { StepsModule } from 'primeng/steps';
import { CreateDefinitionComponent } from './create-definition/create-definition.component';
import { DefinitionInOutComponent } from './definition-in-out/definition-in-out.component';
import { DefinitionJsonUploadComponent } from './definition-json-upload/definition-json-upload.component';
import { DefinitionsOverviewComponent } from './definitions-overview/definitions-overview.component';
import { CorpusFormComponent } from './form/corpus-form/corpus-form.component';
import { DataFormComponent } from './form/data-form/data-form.component';
import { DatafileInfoComponent } from './form/data-form/datafile-info/datafile-info.component';
import { DocumentationFormComponent } from './form/documentation-form/documentation-form.component';
import { MarkdownEditorComponent } from './form/documentation-form/markdown-editor/markdown-editor.component';
import { FieldFormComponent } from './form/field-form/field-form.component';
import { FormFeedbackComponent } from './form/form-feedback/form-feedback.component';
import { ImageUploadComponent } from './form/image-upload/image-upload.component';
import { IndexFormComponent } from './form/index-form/index-form.component';
import { MetaFormComponent } from './form/meta-form/meta-form.component';

@NgModule({
    declarations: [
        CreateDefinitionComponent,
        DatafileInfoComponent,
        DefinitionsOverviewComponent,
        DefinitionInOutComponent,
        DefinitionJsonUploadComponent,
        MetaFormComponent,
        CorpusFormComponent,
        FieldFormComponent,
        DocumentationFormComponent,
        ImageUploadComponent,
        FormFeedbackComponent,
        IndexFormComponent,
        DataFormComponent,
        MarkdownEditorComponent,
    ],
    exports: [
        CreateDefinitionComponent,
        DefinitionsOverviewComponent,
        DefinitionInOutComponent,
        CorpusFormComponent,
    ],
    imports: [
        SharedModule,
        ReactiveFormsModule,
        StepsModule,
        AutoCompleteModule,
        MultiSelectModule,
        DropdownModule,
        QuillModule.forRoot(),
    ],
})
export class CorpusDefinitionsModule {}
