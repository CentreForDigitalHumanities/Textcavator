import { Injectable } from '@angular/core';
import {
    AggregateTermFrequencyParameters,
    Corpus,
    DateTermFrequencyParameters,
    GeoDocument,
    GeoLocation,
    MostFrequentWordsResult,
    NGramRequestParameters,
    QueryModel,
    TaskResult,
    TimeCategory,
} from '@models';
import { ApiService } from './api.service';
import { Observable } from 'rxjs';
import { NgramSettings } from '@models/ngram';

@Injectable({
  providedIn: 'root'
})
export class VisualizationService {

    constructor(
        private apiService: ApiService) {
        window['apiService'] = this.apiService;
    }


    public getWordcloudData(fieldName: string, queryModel: QueryModel, corpus: Corpus, size: number):
        Observable<MostFrequentWordsResult[]> {
        const query = queryModel.toAPIQuery();
        return this.apiService.wordCloud({
            ...query,
            corpus: corpus.name,
            field: fieldName,
            size,
        });
    }

    public getGeoData(fieldName: string, queryModel: QueryModel, corpus: Corpus):
        Observable<GeoDocument[]> {
        const query = queryModel.toAPIQuery();
        return this.apiService.geoData({
            ...query,
            corpus: corpus.name,
            field: fieldName,
        });
    }

    public async getGeoCentroid(fieldName: string, corpus: Corpus):
    Promise<GeoLocation> {
    return this.apiService.geoCentroid({
        corpus: corpus.name,
        field: fieldName,
    });
}

    public makeAggregateTermFrequencyParameters(
        corpus: Corpus, queryModel: QueryModel, fieldName: string, bins: {fieldValue: string|number; size: number}[],
    ): AggregateTermFrequencyParameters {
        const query = queryModel.toAPIQuery();
        return {
            corpus_name: corpus.name,
            ...query,
            field_name: fieldName,
            bins: bins.map(bin => ({field_value: bin.fieldValue, size: bin.size})),
        };
    }

    public async aggregateTermFrequencySearch(
        corpus: Corpus, queryModel: QueryModel, fieldName: string, bins: {fieldValue: string|number; size: number}[],
    ): Promise<TaskResult> {
        const params = this.makeAggregateTermFrequencyParameters(corpus, queryModel, fieldName, bins);
        return this.apiService.getAggregateTermFrequency(params);
    }

    public makeDateTermFrequencyParameters(
        corpus: Corpus, queryModel: QueryModel, fieldName: string, bins: {size: number; start_date: Date; end_date?: Date}[],
        unit: TimeCategory,
    ): DateTermFrequencyParameters {
        const query = queryModel.toAPIQuery();
        return {
            corpus_name: corpus.name,
            ...query,
            field_name: fieldName,
            bins: bins.map(bin => ({
                start_date: bin.start_date.toISOString().slice(0, 10),
                end_date: bin.end_date ? bin.end_date.toISOString().slice(0, 10) : null,
                size: bin.size,
            })),
            unit,
        };
    }

    public makeNgramRequestParameters(
        corpus: Corpus,
        queryModel: QueryModel,
        field: string,
        params: NgramSettings,
        dateField: string
    ): NGramRequestParameters {
        const query = queryModel.toAPIQuery();
        return {
            ...query,
            corpus_name: corpus.name,
            field,
            mode: params.mode,
            ngram_size: params.size,
            term_position: params.positions,
            freq_compensation: params.freqCompensation,
            subfield: params.analysis,
            max_size_per_interval: params.maxDocuments,
            number_of_ngrams: params.numberOfNgrams,
            date_field: dateField
        };
    }

    public async dateTermFrequencySearch<TKey>(
        corpus: Corpus, queryModel: QueryModel, fieldName: string, bins: {size: number; start_date: Date; end_date?: Date}[],
        unit: TimeCategory,
    ): Promise<TaskResult> {
        const params = this.makeDateTermFrequencyParameters(corpus, queryModel, fieldName, bins, unit);
        return this.apiService.getDateTermFrequency(params);
    }

    getNgramTasks(queryModel: QueryModel, corpus: Corpus, field: string, params: NgramSettings, dateField: string): Promise<TaskResult> {
        const ngramRequestParams = this.makeNgramRequestParameters(corpus, queryModel, field, params, dateField);
        return this.apiService.ngramTasks(ngramRequestParams);
    }


}
