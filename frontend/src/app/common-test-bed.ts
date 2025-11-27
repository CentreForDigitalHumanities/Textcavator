import { TestBed } from '@angular/core/testing';
import { ElementRef } from '@angular/core'
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import {FontAwesomeTestingModule} from '@fortawesome/angular-fontawesome/testing';

import { appRoutes, imports, providers } from './app.module';

import { ApiServiceMock } from '../mock-data/api';
import { AuthServiceMock } from '../mock-data/auth';
import { CorpusServiceMock } from '../mock-data/corpus';
import { DialogServiceMock } from '../mock-data/dialog';
import { ElasticSearchServiceMock } from '../mock-data/elastic-search';
import { EntityServiceMock } from '../mock-data/entity';
import { MockCorpusResponse } from '../mock-data/corpus-response';
import { SearchServiceMock } from '../mock-data/search';
import { ApiService, AuthService, CorpusService, DialogService, SearchService } from './services';
import { ElasticSearchService } from './services/elastic-search.service';
import { EntityService } from './services/entity.service';
import { WordmodelsService } from './services/wordmodels.service';
import { WordmodelsServiceMock } from '../mock-data/wordmodels';
import { VisualizationService } from './services/visualization.service';
import { VisualizationServiceMock } from '../mock-data/visualization';
import { TagService } from './services/tag.service';
import { TagServiceMock } from '../mock-data/tag';
import { RouterStoreService } from './store/router-store.service';
import { SimpleStore } from './store/simple-store';
import { CorpusDefinitionService } from './corpus-definitions/corpus-definition.service';

export const commonTestBed = () => {
    const filteredImports = imports.filter(value => !(value in provideHttpClient()));
    filteredImports.push(FontAwesomeTestingModule);
    const filteredProviders = providers.filter(provider => !(
        provider in [ApiService, CorpusService, DialogService, ElasticSearchService, SearchService]));
    filteredProviders.push(
        {
            provide: ApiService,
            useValue: new ApiServiceMock({
                ['corpus']: MockCorpusResponse,
            }),
        },
        {
            provide: AuthService, useClass: AuthServiceMock,
        },
        {
            provide: CorpusService, useClass: CorpusServiceMock,
        },
        {
            provide: DialogService, useClass: DialogServiceMock,
        },
        {
            provide: ElasticSearchService, useClass: ElasticSearchServiceMock,
        },
        {
            provide: EntityService, useClass: EntityServiceMock,
        },
        {
            provide: ElementRef, useClass: MockElementRef,
        },
        {
            provide: SearchService, useClass: SearchServiceMock,
        },
        {
            provide: WordmodelsService, useClass: WordmodelsServiceMock,
        },
        {
            provide: VisualizationService, useClass: VisualizationServiceMock,
        },
        {
            provide: TagService, useClass: TagServiceMock,
        },
        {
            provide: RouterStoreService, useClass: SimpleStore,
        },
        {
            provide: CorpusDefinitionService,
        },
        provideRouter(appRoutes)
    );

    return {
        testingModule: TestBed.configureTestingModule({
            imports: filteredImports,
            providers: filteredProviders
        })
    };
};

export class MockElementRef {
 nativeElement = {};
}
