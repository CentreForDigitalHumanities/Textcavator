import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { CorpusFilterComponent } from './corpus-filter.component';
import { commonTestBed } from '@app/common-test-bed';
import { corpusFactory } from '@mock-data/corpus';
import { Corpus } from '@models';

describe('CorpusFilterComponent', () => {
    let component: CorpusFilterComponent;
    let fixture: ComponentFixture<CorpusFilterComponent>;
    let corpus1;
    let corpus2;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(CorpusFilterComponent);
        component = fixture.componentInstance;

        corpus1 = corpusFactory();

        corpus2 = corpusFactory();
        corpus2.languages = ['English', 'French'];
        corpus2.category = 'Poems';
        corpus2.minYear = 1850;
        corpus2.maxYear = 2000;

        component.corpora = [corpus1, corpus2];
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should filter corpora', async () => {
        let result: Corpus[];
        component.filtered.subscribe(data => result = data);

        const filterResult = async (language: string | null, category: string | null, minYear: number, maxYear: number) => {
            component.form.setValue({
                language, category, minYear, maxYear
            });
            await fixture.whenStable();
            return result;
        };

        expect(await filterResult('English', null, 1800, 2000))
            .toEqual([corpus1, corpus2]);
        expect(await filterResult('French', null, 1800, 2000))
            .toEqual([corpus2]);
        expect(await filterResult(null, null, 1800, 2000))
            .toEqual([corpus1, corpus2]);
        expect(await filterResult(null, 'Books', 1800, 2000))
            .toEqual([corpus1]);
        expect(await filterResult('French', 'Poems', 1800, 2000))
            .toEqual([corpus2]);
        expect(await filterResult('French', 'Books', 1800, 2000))
            .toEqual([]);
        expect(await filterResult(null, null, 1920, 2000))
            .toEqual([corpus2]);
        expect(await filterResult(null, null, 1820, 2000))
            .toEqual([corpus1, corpus2]);
        expect(await filterResult(null, null, 1800, 1830))
            .toEqual([corpus1]);
    });
});
