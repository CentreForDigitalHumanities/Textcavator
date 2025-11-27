import { TestBed } from '@angular/core/testing';
import { ElasticSearchServiceMock } from '@mock-data/elastic-search';
import { ApiServiceMock } from '@mock-data/api';
import { ApiService } from './api.service';
import { ElasticSearchService } from './elastic-search.service';

import { VisualizationService } from './visualization.service';

describe('VisualizationService', () => {
  let service: VisualizationService;

  beforeEach(() => {
    TestBed.configureTestingModule({
        providers: [
            { provide: ApiService, useValue: new ApiServiceMock() },
            { provide: ElasticSearchService, useValue: new ElasticSearchServiceMock() },
        ]
    });
    service = TestBed.inject(VisualizationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
