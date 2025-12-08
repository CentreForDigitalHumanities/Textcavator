import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DocumentationFormComponent } from './documentation-form.component';
import { SharedModule } from '@shared/shared.module';
import { CorpusDefinitionService } from 'app/corpus-definitions/corpus-definition.service';
import { ApiService, CorpusService } from '@services';
import { ApiServiceMock } from 'mock-data/api';
import { CorpusDefinition } from '@models/corpus-definition';
import { ReactiveFormsModule } from '@angular/forms';
import { FormFeedbackComponent } from '../form-feedback/form-feedback.component';
import { MarkdownEditorComponent } from './markdown-editor/markdown-editor.component';
import { QuillModule } from 'ngx-quill';
import { CorpusServiceMock } from '@mock-data/corpus';


describe('DocumentationFormComponent', () => {
    let component: DocumentationFormComponent;
    let fixture: ComponentFixture<DocumentationFormComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [
                DocumentationFormComponent,
                FormFeedbackComponent,
                MarkdownEditorComponent,
            ],
            imports: [SharedModule, ReactiveFormsModule, QuillModule],
            providers: [
                CorpusDefinitionService,
                { provide: ApiService, useClass: ApiServiceMock },
                { provide: CorpusService, useClass: CorpusServiceMock },
            ]

        })
            .compileComponents();

        const apiService = TestBed.inject(ApiService);
        const definitionService = TestBed.inject(CorpusDefinitionService);
        const corpusService = TestBed.inject(CorpusService);
        const corpus = new CorpusDefinition(apiService, corpusService, 1);
        definitionService.setCorpus(corpus);

        fixture = TestBed.createComponent(DocumentationFormComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
