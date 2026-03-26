from datetime import datetime
import os
from typing import List
import csv

from ianalyzer_readers.extract import CSV
from addcorpus.python_corpora.corpus import FieldDefinition, CSVCorpusDefinition
from addcorpus.es_mappings import (
    date_mapping, main_content_mapping, keyword_mapping, non_indexed_text_mapping,
)
from addcorpus.python_corpora.filters import MultipleChoiceFilter, DateFilter
from addcorpus.es_settings import es_settings

here = os.path.abspath(os.path.dirname(__file__))

def parse_multivalue(input: str) -> List[str]:
    if input:
        reader = csv.reader([input], delimiter=';')
        return next(reader)


class AnnotatedMockCorpus(CSVCorpusDefinition):
    title = 'Annotated Test Corpus'
    description = 'Test corpus with Named Entity annotations'
    min_date = datetime(year=1814, month=1, day=1)
    max_date = datetime(year=2000, month=12, day=31)
    data_directory = os.path.join(here, 'source_data')
    languages = ['nl']
    category = 'oration'

    es_settings = es_settings(['nl'])

    def sources(self, *args, **kwargs):
        for csv_file in os.listdir(self.data_directory):
            yield os.path.join(self.data_directory, csv_file)

    id = FieldDefinition(
        name='id',
        display_name='ID',
        es_mapping=keyword_mapping(),
        extractor=CSV('id')
    )

    date = FieldDefinition(
        name='date',
        display_name='Date',
        es_mapping=date_mapping(),
        visualizations=['resultscount', 'termfrequency'],
        search_filter=DateFilter(lower=min_date,upper=max_date),
        extractor=CSV('date'),
        results_overview=True,
    )

    content = FieldDefinition(
        name='content',
        display_name='Content',
        display_type='text_content',
        es_mapping=main_content_mapping(True, True, True, 'nl'),
        extractor=CSV('content'),
        language='nl',
        results_overview=True,
    )

    content_annotated = FieldDefinition(
        name='content:ner',
        display_type='text_content',
        hidden=True,
        searchable=False,
        es_mapping=non_indexed_text_mapping(),
        extractor=CSV('content_annotated')
    )

    named_entity_fields = [
        FieldDefinition(
                name=f'{entity_type}:ner-kw',
                display_name=f'Named entities: {entity_type}',
                searchable=True,
                es_mapping=keyword_mapping(enable_full_text_search=True),
                search_filter=MultipleChoiceFilter(
                    description='Filter on named entities mentioned in the speech',
                ),
                extractor=CSV(f'entities_{entity_type}', transform=parse_multivalue)
        )
        for entity_type in ['person', 'location', 'organization', 'miscellaneous']
    ]

    fields = [id, date, content, content_annotated, *named_entity_fields]
