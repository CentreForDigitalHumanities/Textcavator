import { PageResultsParameters } from '../app/models/page-results';
import { SearchFilter } from '../app/models/field-filter';
import { Corpus, CorpusField, QueryModel, SearchResults } from '../app/models/index';
import { Aggregator } from '../app/models/aggregation';
import { makeDocument } from './constructor-helpers';

export class SearchServiceMock {
    public async aggregateSearch(corpus: Corpus, queryModel: QueryModel, aggregator: Aggregator<any>): Promise<any> {
        return [
            {
                key: '1999',
                doc_count: 200
            }, {
                key: '2000',
                doc_count: 300
            }, {
                key: '2001',
                doc_count: 400
            }
        ];
    }

    public async getRelatedWords() {}

    createQueryModel(
        corpus: Corpus,
        queryText: string = '', fields: CorpusField[] | null = null, filters: SearchFilter[] = []): QueryModel {
        const model = new QueryModel(corpus);
        model.setParams({
            queryText,
            searchFields: fields
        });
        filters.forEach(model.addFilter);

        return model;
    }

    loadResults(queryModel: QueryModel, resultsParams: PageResultsParameters): Promise<SearchResults> {
        const doc = makeDocument();
        return Promise.resolve({
            documents: [doc],
            total: { value: 1, relation: 'eq' }
        });
    }
}
