import os
from datetime import date

from textcavator_readers.readers.csv import CSVReader
from textcavator_readers.readers.xml import XMLReader
from textcavator_readers.extract import CSV, XML, Metadata
from textcavator_readers.xml_tag import Tag
from textcavator_readers.readers.core import Field

from addcorpus.es_mappings import keyword_mapping, text_mapping, int_mapping, main_content_mapping
from addcorpus.python_corpora.corpus import CorpusDefinition, FieldDefinition


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
        ),
        FieldDefinition(
            name='author',
            es_mapping=keyword_mapping(False),
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('author'), Tag('name'),
                toplevel=True,
            )
        ),
        FieldDefinition(
            name='editor',
            es_mapping=keyword_mapping(False),
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('editor'), Tag('name'),
                toplevel=True,
            )
        ),
        FieldDefinition(
            name='id',
            es_mapping=keyword_mapping(),
            extractor=XML(
                attribute='id',
            )
        ),
        FieldDefinition(
            name='pub_year',
            es_mapping=int_mapping(),
            extractor=Metadata('year'),
        ),
        FieldDefinition(
            name='pub_place',
            es_mapping=keyword_mapping(False),
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('imprint'), Tag('pubPlace'),
                toplevel=True,
            )
        ),
        FieldDefinition(
            name='body',
            display_type='text_content',
            es_mapping=main_content_mapping(True, False, False),
            extractor=XML(
                Tag('body'),
                flatten=True,
            )
        ),
        FieldDefinition(
            name='body_langs',
            es_mapping=keyword_mapping(False),
            extractor=XML(
                Tag('body'),
                Tag(lambda tag: tag.has_attr('lang')),
                multiple=True,
                attribute='lang',
                transform=lambda values: list(set(values))
            )
        ),
        FieldDefinition(
            name='translation_nl',
            display_type='text_content',
            es_mapping=main_content_mapping(True, False, False, 'nl'),
            language='nl',
            extractor=XML(
                Tag('back'),
                Tag(attrs={'type': 'translations'}),
                Tag(attrs={'lang': 'dut', 'type': 'translation'}),
                flatten=True,
                multiple=True,
            )
        ),
        FieldDefinition(
            name='translation_en',
            display_type='text_content',
            es_mapping=main_content_mapping(True, False, False, 'en'),
            language='en',
            extractor=XML(
                Tag('back'),
                Tag(attrs={'type': 'translations'}),
                Tag(attrs={'lang': 'eng', 'type': 'translation'}),
                flatten=True,
                multiple=True,
            )
        )
    ]

