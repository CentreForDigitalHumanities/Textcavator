import os
from datetime import date
import re

import bs4
from textcavator_readers.readers.csv import CSVReader
from textcavator_readers.readers.xml import XMLReader
from textcavator_readers.extract import CSV, XML, Metadata
from textcavator_readers.xml_tag import Tag
from textcavator_readers.readers.core import Field

from addcorpus.es_mappings import keyword_mapping, text_mapping, int_mapping, main_content_mapping
from addcorpus.python_corpora.corpus import CorpusDefinition, FieldDefinition
from addcorpus.python_corpora.filters import MultipleChoiceFilter, RangeFilter
from corpora.emblems.xml_utils import extract_text

class EmblemsIndexReader(CSVReader):
    data_directory = None
    required_field = 'Author'

    def __init__(self, data_directory):
        self.data_directory = data_directory

    def sources(self, **kwargs):
        return [
            os.path.join(self.data_directory, 'index.csv')
        ]

    fields = [
        Field(
            name='author',
            extractor=CSV('Author'),
        ),
        Field(
            name='title',
            extractor=CSV('Title'),
        ),
        Field(
            name='year',
            extractor=CSV('Year', transform=int),
        ),
        Field(
            name='id',
            extractor=CSV('ID'),
        ),
    ]


class Emblems(CorpusDefinition, XMLReader):
    title = 'Emblem Project Utrecht'
    description = 'Dutch Love Emblems of the Seventeenth Century'
    category = 'poetry'
    min_date = date(1601, 1, 1)
    max_date = date(1724, 12, 31)
    languages = ['nl', 'lat', 'fr', 'it', 'en', 'es', 'de']

    tag_top = Tag('TEI.2')
    tag_entry = Tag('text', attrs={'type': ['front', 'emblem']})


    def data_from_file(self, filename):
        # override to remove <!DOCTYPE section from XML content before parsing;
        # (otherwise the file does not parse)
        with open(filename, 'r') as f:
            content = f.read()
            clean = re.sub(r'<!DOCTYPE .*\[.*\]>', '', content, 1, flags=re.DOTALL)
            return bs4.BeautifulSoup(clean, 'lxml-xml')


    def sources(self, **kwargs):
        index_reader = EmblemsIndexReader(self.data_directory)
        for doc in index_reader.documents():
            filename = doc['id'] + '.xml'
            path = os.path.join(self.data_directory, 'xml', filename)
            yield path, doc

    fields = [
        FieldDefinition(
            name='title',
            display_name='Title',
            es_mapping=keyword_mapping(True),
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('title'),
                toplevel=True,
            ),
            results_overview=True,
            visualizations=['resultscount', 'termfrequency'],
            search_filter=MultipleChoiceFilter(),
        ),
        FieldDefinition(
            name='author',
            display_name='Author',
            es_mapping=keyword_mapping(False),
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('author'), Tag('name'),
                toplevel=True,
            ),
            results_overview=True,
            visualizations=['resultscount', 'termfrequency'],
            search_filter=MultipleChoiceFilter(),
        ),
        FieldDefinition(
            name='editor',
            display_name='Editor',
            es_mapping=keyword_mapping(False),
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('editor'), Tag('name'),
                toplevel=True,
            ),
            search_filter=MultipleChoiceFilter(),
        ),
        FieldDefinition(
            name='id',
            display_name='ID',
            es_mapping=keyword_mapping(),
            extractor=XML(
                attribute='id',
            )
        ),
        FieldDefinition(
            name='pub_year',
            display_name='Year',
            es_mapping=int_mapping(),
            extractor=Metadata('year'),
            results_overview=True,
            visualizations=['resultscount', 'termfrequency'],
            search_filter=RangeFilter(lower=1601, upper=1724),
        ),
        FieldDefinition(
            name='pub_place',
            display_name='Place of publication',
            es_mapping=keyword_mapping(False),
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('imprint'), Tag('pubPlace'),
                toplevel=True,
            ),
            visualization=['resultscount', 'termfrequency'],
            search_filter=MultipleChoiceFilter(),
        ),
        FieldDefinition(
            name='content',
            display_name='Content',
            display_type='text_content',
            es_mapping=main_content_mapping(True, False, False),
            extractor=XML(
                Tag('body'),
                extract_soup_func=extract_text,
            ),
            results_overview=True,
            search_field_core=True,
            csv_core=True,
            visualizations=['wordcloud']
        ),
        FieldDefinition(
            name='body_langs',
            display_name='Languages',
            es_mapping=keyword_mapping(False),
            extractor=XML(
                Tag('body'),
                Tag(lambda tag: tag.has_attr('lang')),
                multiple=True,
                attribute='lang',
                transform=lambda values: list(set(values))
            ),
            search_filter=MultipleChoiceFilter(),
        ),
        FieldDefinition(
            name='translation_nl',
            display_name='Translation (Dutch)',
            display_type='text_content',
            es_mapping=main_content_mapping(True, False, False, 'nl'),
            language='nl',
            extractor=XML(
                Tag('back'),
                Tag(attrs={'type': 'translations'}),
                Tag(attrs={'lang': 'dut', 'type': 'translation'}),
                flatten=True,
                multiple=True,
            ),
            search_field_core=True,
        ),
        FieldDefinition(
            name='translation_en',
            display_name='Translation (English)',
            display_type='text_content',
            es_mapping=main_content_mapping(True, False, False, 'en'),
            language='en',
            extractor=XML(
                Tag('back'),
                Tag(attrs={'type': 'translations'}),
                Tag(attrs={'lang': 'eng', 'type': 'translation'}),
                flatten=True,
                multiple=True,
            ),
            search_field_core=True,
        )
    ]

