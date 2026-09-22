import os

from textcavator_readers.readers.csv import CSVReader
from textcavator_readers.readers.xml import XMLReader
from textcavator_readers.extract import CSV, XML, Metadata
from textcavator_readers.xml_tag import Tag
from textcavator_readers.readers.core import Field

# TODO: do not hardcode
DATA_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'tests/data'
)


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



class EmblemsDataReader(XMLReader):
    data_directory = DATA_DIR
    tag_top = Tag('TEI.2')
    tag_entry = Tag('text', attrs={'type': ['front', 'emblem']})

    def sources(self, **kwargs):
        index_reader = EmblemsIndexReader(self.data_directory)
        for doc in index_reader.documents():
            filename = doc['id'] + '.xml'
            path = os.path.join(self.data_directory, 'xml', filename)
            yield path, doc

    fields = [
        Field(
            name='title',
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('title'),
                toplevel=True,
            ),
        ),
        Field(
            name='author',
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('author'), Tag('name'),
                toplevel=True,
            )
        ),
        Field(
            name='editor',
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('editor'), Tag('name'),
                toplevel=True,
            )
        ),
        Field(
            name='pub_year',
            extractor=Metadata('year'),
        ),
        Field(
            name='pub_place',
            extractor=XML(
                Tag('teiHeader'), Tag('sourceDesc'), Tag('imprint'), Tag('pubPlace'),
                toplevel=True,
            )
        ),
        Field(
            name='body',
            extractor=XML(
                Tag('body'),
                flatten=True,
            )
        ),
        Field(
            name='body_langs',
            extractor=XML(
                Tag('body'),
                Tag(lambda tag: tag.has_attr('lang')),
                multiple=True,
                attribute='lang',
                transform=lambda values: list(set(values))
            )
        ),
        Field(
            name='translation_nl',
            extractor=XML(
                Tag('back'),
                Tag(attrs={'type': 'translations'}),
                Tag(attrs={'lang': 'dut', 'type': 'translation'}),
                flatten=True,
                multiple=True,
            )
        ),
        Field(
            name='translation_en',
            extractor=XML(
                Tag('back'),
                Tag(attrs={'type': 'translations'}),
                Tag(attrs={'lang': 'eng', 'type': 'translation'}),
                flatten=True,
                multiple=True,
            )
        )
    ]

