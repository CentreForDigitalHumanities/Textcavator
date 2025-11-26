import { APICorpusDefinition, CorpusDataFile} from '../app/models/corpus-definition';

export const corpusDefinitionFactory = (): APICorpusDefinition => ({
    name: 'test',
    meta: {
        title: 'Test corpus',
        description: 'JSON corpus definition for testing',
        category: 'book',
        date_range: {
            min: 1800,
            max: 1900,
        },
        languages: ['en'],
    },
    source_data: {
        type: 'csv'
    },
    fields: [
        {
            name: 'content',
            display_name: 'Content',
            description: 'Main text content',
            type: 'text_content',
            options: {
                search: true,
                filter: 'none',
                visualize: true,
                preview: true,
                sort: false,
                hidden: false,
            },
            extract: {
                column: 'content'
            }
        },
        {
            name: 'date',
            display_name: 'Date',
            description: 'Date on which the text was published',
            type: 'date',
            options: {
                search: false,
                filter: 'show',
                visualize: true,
                preview: true,
                sort: true,
                hidden: false,
            },
            extract: {
                column: 'date'
            }
        }
    ]
});

export const dataFileFactory = (): CorpusDataFile => ({
    id: 0,
    corpusID: 0,
    file: '',
    is_sample: true,
    confirmed: false,
    csv_info: {
        n_rows: 3,
        fields: [
            { name: 'date', type: 'date' },
            { name: 'genre', type: 'text_metadata' },
            { name: 'title', type: 'text_metadata' },
            { name: 'content', type: 'text_content' },
            { name: 'url', type: 'url' },
        ],
        delimiter: ',',
    },
});
