import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { By } from '@angular/platform-browser';

import { DocumentPopupComponent } from './document-popup.component';
import { commonTestBed } from '@app/common-test-bed';
import { makeDocument } from '@mock-data/constructor-helpers';
import { corpusFactory } from '@mock-data/corpus';
import { DocumentPage } from '@models/document-page';
import { QueryModel } from '@models';


describe('DocumentPopupComponent', () => {
    let component: DocumentPopupComponent;
    let fixture: ComponentFixture<DocumentPopupComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DocumentPopupComponent);
        component = fixture.componentInstance;
        const corpus = corpusFactory();
        const document = makeDocument(
            { genre: 'Science Fiction', content: 'Bleep bloop', date: '1950-01-01' },
            corpus,
        );
        component.document = document;
        component.page = new DocumentPage([document], 1, corpus.fields);
        component.queryModel = new QueryModel(corpus);
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('does not show the NER toggle for corpora without named entities', () => {
        expect(fixture.debugElement.query(By.css('ia-entity-toggle'))).toBeFalsy();
    });

    it('shows the NER toggle for corpora with named entities', () => {
        const setModel = component.queryModel;

        const corpusWithEntities = corpusFactory();
        corpusWithEntities.hasNamedEntities = true;

        const queryModel = new QueryModel(corpusWithEntities);
        component.queryModel = queryModel;
        component.ngOnChanges({queryModel: {previousValue: setModel, currentValue: queryModel, firstChange: false, isFirstChange: null}});
        fixture.detectChanges();
        expect(fixture.debugElement.query(By.css('ia-entity-toggle'))).toBeTruthy();
    });
});
