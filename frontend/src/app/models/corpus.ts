import * as _ from 'lodash';
import { AdHocFilter, BooleanFilter, DateFilter, MultipleChoiceFilter, RangeFilter, SearchFilter } from './field-filter';
import { FieldFilterOptions } from './field-filter-options';
import { SortState } from './sort';
import { Store } from '../store/types';
import { SimpleStore } from '../store/simple-store';

// corresponds to the corpus definition on the backend.
export class Corpus {
    constructor(
        public id: number,
        /**
         * Internal name for referring to this corpus e.g. in URLs.
         */
        public name: string,
        /**
         * Human readable title of this corpus.
         */
        public title: string,
        /**
         * Description of the corpus to show to users.
         */
        public description: string,
        public index: string,
        public fields: CorpusField[],
        public minYear: number,
        public maxYear: number,
        public scanImageType: string,
        public allowImageDownload: boolean,
        public wordModelsPresent: boolean,
        public languages: string[],
        public category: string,
        public hasNamedEntities: boolean,
        public documentContext?: DocumentContext,
        public defaultSort?: SortState,
        public languageField?: CorpusField,
        public editable?: boolean,
    ) { }

    get displayLanguages(): string {
        return this.languages.join(', ');
    }
}


export interface DocumentContext {
    contextFields: CorpusField[];
    sortField?: CorpusField;
    sortDirection?: 'asc'|'desc';
    displayName: string;
}


export type FieldDisplayType =
    'text_content' | 'keyword' | 'integer' | 'text' | 'date' | 'date_range' | 'boolean'
    | 'url' | 'geo_point';


export interface APICorpus {
    id: number;
    name: string;
    editable: boolean;
    allow_image_download: boolean;
    category: string;
    description: string;
    document_context:APIDocumentContext;
    es_alias: string;
    es_index: string;
    languages: string[];
    min_year: number;
    max_year: number;
    scan_image_type: string;
    title: string;
    word_models_present: boolean;
    default_sort: {
        field: string;
        ascending: boolean;
    };
    language_field: string;
    fields: ApiCorpusField[];
    has_named_entities: boolean;
}

export interface APIDocumentContext {
    context_fields: string[] | null;
    sort_field: string | null;
    context_display_name: string | null;
    sort_direction: 'string' | null;
}


/** Corpus field info as sent by the backend api */
export interface ApiCorpusField {
    name: string;
    display_name: string;
    display_type: FieldDisplayType;
    description: string;
    search_filter: FieldFilterOptions | null;
    results_overview: boolean;
    csv_core: boolean;
    search_field_core: boolean;
    visualizations: string[];
    visualization_sort: string | null;
    es_mapping: any;
    indexed: boolean;
    hidden: boolean;
    required: boolean;
    sortable: boolean;
    searchable: boolean;
    downloadable: boolean;
    language: string;
}

export class CorpusField {
    description: string;
    displayName: string;
    /**
     * How the field value should be displayed.
     * text_content: Main text content of the document
     */
    displayType: FieldDisplayType;
    resultsOverview?: boolean;
    csvCore?: boolean;
    searchFieldCore?: boolean;
    visualizations?: string[];
    visualizationSort?: string;
    multiFields?: string[];
    fastVectorHighlight?: boolean;
    hidden: boolean;
    sortable: boolean;
    searchable: boolean;
    downloadable: boolean;
    name: string;
    filterOptions: FieldFilterOptions;
    mappingType: 'text' | 'keyword' | 'boolean' | 'date' | 'integer' | 'geo_point' | null;
    language: string;

    constructor(data: ApiCorpusField) {
        this.description = data.description;
        this.displayName = data.display_name || data.name;
        this.displayType = data.display_type || data['es_mapping']?.type;
        this.resultsOverview = data.results_overview;
        this.csvCore = data.csv_core;
        this.searchFieldCore = data.search_field_core;
        this.visualizations = data.visualizations;
        this.visualizationSort = data.visualization_sort;
        this.multiFields = data['es_mapping']?.fields
            ? Object.keys(data['es_mapping'].fields)
            : undefined;
        this.fastVectorHighlight = data['es_mapping']?.term_vector?.startsWith('with_positions_offsets')
        this.hidden = data.hidden;
        this.sortable = data.sortable;
        this.searchable = data.searchable;
        this.downloadable = data.downloadable;
        this.name = data.name;
        this.filterOptions = data['search_filter'];
        this.mappingType = data.es_mapping?.type;
        this.language = data.language || undefined;
    }

    /** make a SearchFilter for this field */
    makeSearchFilter(store?: Store): SearchFilter {
		const filterClasses = {
			DateFilter,
			MultipleChoiceFilter,
			BooleanFilter,
			RangeFilter,
		};
		const Filter = _.get(
			filterClasses,
			this.filterOptions?.name,
			AdHocFilter
		);
        store = store || new SimpleStore();
		return new Filter(store, this);
	}
}

export interface CorpusDocumentationPage {
    id: number;
    corpus: string;
    type: string;
    content: string;
    index: number;
}

