import { ComponentFixture, TestBed } from '@angular/core/testing';

import { decreaseHeaderLevels, increaseHeaderLevels, MarkdownEditorComponent } from './markdown-editor.component';
import { Component } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { SharedModule } from '@shared/shared.module';
import { QuillModule } from 'ngx-quill';
import { CorpusDefinitionsModule } from '@app/corpus-definitions/corpus-definitions.module';
import { CommonModule } from '@angular/common';

const contentH1H2 = `# Bla
Bla bla

## Bla bla bla
Bla bla bla

# Bla
Bla bla bla`;

const contentH2H3 = `## Bla
Bla bla

### Bla bla bla
Bla bla bla

## Bla
Bla bla bla`;

describe('increaseHeaderLevels', () => {
    it('should adjust header levels', () => {
        expect(increaseHeaderLevels(contentH1H2)).toEqual(contentH2H3)
    });

    it('should not increase beyond 6', () => {
        const content = '###### Tiny header'
        expect(increaseHeaderLevels(content)).toEqual(content);
    });
});

describe('decreaseHeaderLevels', () => {
    it('should adjust header levels', () => {

        expect(decreaseHeaderLevels(contentH2H3)).toEqual(contentH1H2);
    });

    it('should not decrease beyond 1', () => {
        const content = '# Big header'
        expect(decreaseHeaderLevels(content)).toEqual(content);
    });
});

@Component({
    template: `
    <ia-markdown-editor [formControl]="control"/>
    `,
    imports: [MarkdownEditorComponent, ReactiveFormsModule, CommonModule],
})
class EditorTestComponent {
    control = new FormControl<string>('');
}

describe('MarkdownEditorComponent', () => {
    let component: EditorTestComponent;
    let fixture: ComponentFixture<EditorTestComponent>;

    beforeEach(async () => {
        fixture = TestBed.createComponent(EditorTestComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

});
