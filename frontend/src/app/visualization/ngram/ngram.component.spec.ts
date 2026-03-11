import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { By } from '@angular/platform-browser';

import { QueryModel } from '@models';
import { corpusFactory } from '@mock-data/corpus';
import { commonTestBed } from '@app/common-test-bed';
import { NgramComponent } from './ngram.component';
import { ApiService, VisualizationService } from '@services';
import { ApiServiceMock, fakeNgramResult } from '@mock-data/api';
import { VisualizationServiceMock } from '@mock-data/visualization';
import { Subject } from 'rxjs';
import { NgramSettings } from '@models/ngram';


describe('NgramComponent', () => {
    let component: NgramComponent;
    let fixture: ComponentFixture<NgramComponent>;
    let apiService: ApiServiceMock;
    let visualizationService: VisualizationService;
    let cacheKey = 'o:n,s:2,p:any,c:false,a:none,m:50,n:10';
    let defaultSettings: NgramSettings = {
        mode: 'ngrams',
        size: 2,
        positions: 'any',
        freqCompensation: false,
        analysis: 'none',
        maxDocuments: 50,
        numberOfNgrams: 10,
    };
    let element: HTMLElement;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        apiService = new ApiServiceMock({});
        visualizationService = new VisualizationServiceMock() as any;
        spyOn(visualizationService, 'getNgramTasks').and.callThrough();
        spyOn(apiService, 'abortTasks').and.callThrough();
        fixture = TestBed.overrideComponent(NgramComponent, {
            set: {
                providers: [
                    { provide: ApiService, useValue: apiService },
                    { provide: VisualizationService, useValue: visualizationService }
                ]
            }
        }).createComponent(NgramComponent);
        component = fixture.componentInstance;
        const queryModel = new QueryModel(corpusFactory());
        queryModel.setQueryText('testing');
        component.stopPolling$ = new Subject();
        component.queryModel = queryModel;
        component.corpus = queryModel.corpus;
        component.visualizedField = { name: 'speech' } as any;
        component.dateField = queryModel.corpus.fields[2];
        component.allDateFields = [component.dateField];
        component.asTable = false;
        component.palette = ['yellow', 'blue'];
        fixture.detectChanges();
        element = fixture.nativeElement;
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should initialize ngramParameters with default values', () => {
        expect(component.ngramParameters.state$.value).toEqual(defaultSettings);
    });

    it('should switch labels in size selection', () => {
        const label = element.querySelector('#label-size');
        const dropdownLabel = (label.nextSibling as HTMLElement).querySelector('[iaDropdownLabel]')
        expect(label.textContent.trim()).toBe('Length of n-gram');
        expect(dropdownLabel.textContent.trim()).toBe('bigrams');

        component.onParameterChange('mode', 'collocates');
        fixture.detectChanges();
        expect(label.textContent.trim()).toBe('Maximum distance');
        expect(dropdownLabel.textContent.trim()).toBe('1');

        component.onParameterChange('size', 3);
        fixture.detectChanges();
        expect(dropdownLabel.textContent.trim()).toBe('2');

        component.onParameterChange('mode', 'ngrams');
        fixture.detectChanges();
        expect(dropdownLabel.textContent.trim()).toBe('trigrams');
    });

    it('should not abort tasks when `onParameterChange` is triggered during initialization', () => {
        spyOn(component.stopPolling$, 'next');
        component.onParameterChange('size', 2);
        expect(component.stopPolling$.next).not.toHaveBeenCalled();
    });

    it('should stop polling and abort running tasks when changing settings', () => {
        const dropdown = fixture.debugElement.query(By.css('ia-dropdown'));
        const changeSizeDropdown = (value: number) => {
            const eventObj = { parameter: 'size', value };
            dropdown.triggerEventHandler('onChange', eventObj);
        };
        spyOn(component.stopPolling$, 'next');
        changeSizeDropdown(10);
        expect(component.stopPolling$.next).toHaveBeenCalled();
        component.dataHasLoaded = false; // fake working response
        expect(component.tasksToCancel).toBeUndefined();
    });

    it('should stop polling and abort running tasks on destroy', () => {
        spyOn(component.stopPolling$, 'next');
        component.ngOnDestroy();
        expect(component.stopPolling$.next).toHaveBeenCalled();
        component.dataHasLoaded = false; // fake working response
        expect(component.tasksToCancel).toBeUndefined();
    });

    it('should send a new ngram request after confirmed changes', () => {
        component.confirmChanges();
        expect(visualizationService.getNgramTasks).toHaveBeenCalled();
    });

    it('should not send a new ngram request when the result is cached', () => {
        component.resultsCache = { [cacheKey]: fakeNgramResult };
        component.confirmChanges();
        expect(visualizationService.getNgramTasks).not.toHaveBeenCalled();
    });

});
