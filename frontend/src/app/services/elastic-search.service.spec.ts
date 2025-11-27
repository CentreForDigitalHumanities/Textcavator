import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ElasticSearchService, SearchResponse } from './elastic-search.service';
import { QueryModel } from '@models';
import { corpusFactory } from '@mock-data/corpus';
import { EntityService } from './entity.service';
import { EntityServiceMock } from '@mock-data/entity';
import { TagServiceMock } from '@mock-data/tag';
import { TagService } from './tag.service';
import { TermsAggregator } from '@models/aggregation';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';


const mockResponse: SearchResponse = {
    took: 4,
    timed_out: false,
    hits: {
        total: {
            value: 20,
            relation: 'eq',
        },
        max_score: 1.0,
        hits: [
            {
                _score: 1.0,
                _id: 'doc1',
                _source: {
                    genre: 'test',
                    content: 'This is a test',
                    date: '1810-01-01',
                }
            }, {
                _score: 0.8,
                _id: 'doc2',
                _source: {
                    genre: 'test',
                    content: 'This is a another test',
                    date: '1820-01-01',
                }
            },
        ],
    },
};

const mockAggregationResponse: SearchResponse = {
    took: 4,
    timed_out: false,
    hits: {
        total: {
            value: 20,
            relation: 'eq',
        },
        max_score: 1.0,
        hits: [],
    },
    aggregations: {
        terms_genre: {
            buckets: [
                { key: 'test', doc_count: 15 },
                { key: 'testtest', doc_count: 5 },
            ]
        }
    }
};

describe('ElasticSearchService', () => {
    let service: ElasticSearchService;
    let httpTestingController: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
    imports: [],
    providers: [
        ElasticSearchService,
        { provide: EntityService, useValue: new EntityServiceMock() },
        { provide: TagService, useValue: new TagServiceMock() },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
});
        service = TestBed.inject(ElasticSearchService);
        httpTestingController = TestBed.inject(HttpTestingController);
    });

    it('should be created',() => {
        expect(service).toBeTruthy();
    });

    it('should make a search request', async () => {
        const corpus = corpusFactory();
        const queryModel = new QueryModel(corpus);
        const size = 2;
        const response = service.loadResults(queryModel, {from: 0, size, sort: [undefined, 'desc']});

        const searchUrl = `/api/es/${corpus.name}/_search`;
        httpTestingController.expectOne(searchUrl).flush(mockResponse);
        httpTestingController.verify();

        const result = await response;
        expect(result.documents.length).toBe(2);
        expect(result.total.value).toBe(20);
    });

    it('should request a document by ID', async () => {
        const corpus = corpusFactory();
        const response = service.getDocumentById('doc1', corpus);

        const searchUrl = `/api/es/${corpus.name}/_search`;
        httpTestingController.expectOne(searchUrl).flush(mockResponse);
        httpTestingController.verify();

        const result = await response;
        expect(result.fieldValue(corpus.fields[1])).toBe('This is a test');
    });

    it('should make an aggregation request', async () => {
        const corpus = corpusFactory();
        const queryModel = new QueryModel(corpus);
        const aggregator = new TermsAggregator(corpus.fields[0], 10);
        const response = service.aggregateSearch(
            corpus,
            queryModel,
            aggregator
        );

        const searchUrl = `/api/es/${corpus.name}/_search`;
        httpTestingController.expectOne(searchUrl).flush(mockAggregationResponse);
        httpTestingController.verify();

        const result = await response;
        expect(result).toBeTruthy();
    });
});
