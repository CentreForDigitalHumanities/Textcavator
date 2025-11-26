import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MetaFormComponent } from './meta-form.component';
import { CorpusDefinitionService } from 'app/corpus-definitions/corpus-definition.service';
import { SlugifyPipe } from '@shared/pipes/slugify.pipe';
import { SharedModule } from '@shared/shared.module';
import { ReactiveFormsModule } from '@angular/forms';
import { CorpusDefinition } from '@models/corpus-definition';
import { ApiService, CorpusService } from '@services';
import { ImageUploadComponent } from '../image-upload/image-upload.component';
import { ApiServiceMock } from 'mock-data/api';
import { FormFeedbackComponent } from '../form-feedback/form-feedback.component';
import { DocumentationFormComponent } from '../documentation-form/documentation-form.component';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { MarkdownEditorComponent } from '../documentation-form/markdown-editor/markdown-editor.component';
import { QuillModule } from 'ngx-quill';
import { CorpusServiceMock } from '@mock-data/corpus';


describe('MetaFormComponent', () => {
    let component: MetaFormComponent;
    let fixture: ComponentFixture<MetaFormComponent>;
    let apiService: ApiService;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [
                MetaFormComponent,
                ImageUploadComponent,
                DocumentationFormComponent,
                FormFeedbackComponent,
                MarkdownEditorComponent,
            ],
            imports: [
                SharedModule,
                ReactiveFormsModule,
                AutoCompleteModule,
                QuillModule,
            ],
            providers: [
                CorpusDefinitionService,
                SlugifyPipe,
                { provide: ApiService, useClass: ApiServiceMock },
                { provide: CorpusService, useClass: CorpusServiceMock },
            ],
        }).compileComponents();

        apiService = TestBed.inject(ApiService);
        const corpusService = TestBed.inject(CorpusService);
        const definitionService = TestBed.inject(CorpusDefinitionService);
        const corpus = new CorpusDefinition(apiService, corpusService, 1);
        definitionService.setCorpus(corpus);

        fixture = TestBed.createComponent(MetaFormComponent);
        component = fixture.componentInstance;
        component.corpus = corpus;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
