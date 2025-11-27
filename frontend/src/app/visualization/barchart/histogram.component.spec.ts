import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { QueryModel } from '@models';

import { commonTestBed } from '@app/common-test-bed';

import { HistogramComponent } from './histogram.component';
import { corpusFactory, keywordFieldFactory } from '@mock-data/corpus';

describe('HistogramCompoment', () => {
    let component: HistogramComponent;
    let fixture: ComponentFixture<HistogramComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(HistogramComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });


    it('should filter text fields', () => {
        component.corpus = corpusFactory();
        component.corpus.fields[0] = keywordFieldFactory(true);

        component.frequencyMeasure = 'documents';

        const query1 = new QueryModel(component.corpus);
        query1.setQueryText('test');

        const query2 = new QueryModel(component.corpus);
        query2.setParams({
            queryText: 'test',
            searchFields: component.corpus.fields.slice(0, 2),
        });

        const queries = [ query1, query2 ];

        queries.forEach(query => {
            const newQuery = component.selectSearchFields(query);
            expect(newQuery.searchFields).toEqual(query.searchFields);
        });

        component.frequencyMeasure = 'tokens';

        queries.forEach(query => {
            const newQuery = component.selectSearchFields(query);
            expect(newQuery.searchFields).toEqual([component.corpus.fields[1]]);
        });
    });

});
