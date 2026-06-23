import re
import os
import os.path as op
import logging
from datetime import datetime

import openpyxl

from ianalyzer_readers.extract import CSV, Metadata
from addcorpus.python_corpora.filters import MultipleChoiceFilter, RangeFilter
from addcorpus.python_corpora.corpus import CSVCorpusDefinition, FieldDefinition, get_deprecated_setting

from addcorpus.es_mappings import main_content_mapping

logger = logging.getLogger('indexing')

class GoodReads(CSVCorpusDefinition):
    """ Home-scraped CSV corpus of GoodReads reviews. """

    # Data overrides from .common.Corpus (fields at bottom of class)
    title = "DIOPTRA-L"
    description = "Goodreads reviews of translated literary texts"

    delimiter = ';'

    min_date=datetime(2007, 1, 1)
    max_date=datetime(2022, 12, 31)

    @property
    def data_directory(self):
        return get_deprecated_setting('GOODREADS_DATA') or super().data_directory

    @property
    def es_index(self):
        return get_deprecated_setting('GOODREADS_ES_INDEX') or 'goodreads'

    image = 'DioptraL.png'
    description_page = 'goodreads.md'
    visualize = []
    languages = ['en', 'es', 'it', 'pt', 'fr',  'nl', 'de', 'ar', 'af', 'sv', ''] # languages with > 1000 docs
    category = 'review'

    # New data members
    non_xml_msg = 'Skipping non-XML file {}'
    non_match_msg = 'Skipping XML file with nonmatching name {}'

    def sources(self, start, end):
        metafile = op.join(self.data_directory, "Reviews_metadata.xlsx")
        wb = openpyxl.load_workbook(filename=metafile)
        sheet = wb['Sheet1']
        for index, row in enumerate(sheet.values):
            if index==0:
                continue
            book_title = row[0]
            book_genre = row[2]
            age_category = row[3]
            original_language = row[4]
            title_dir = re.sub('[^\w .-]', '', book_title).replace(' ', '_')
            path = os.path.join(self.data_directory, title_dir)
            logger.info(path)
            if os.path.isdir(path):
                full_path = os.path.join(path, 'CSV', 'reviews.csv')
                yield full_path, {
                    'book_title': book_title,
                    'book_genre': book_genre,
                    'age_category': age_category,
                    'original_language': original_language
                }

    fields = [
        FieldDefinition(
            name="year",
            display_name="Year",
            description="Year the review was written.",
            extractor=CSV(
                "date",
                transform=lambda x: datetime.strptime(x, "%b %d, %Y").strftime("%Y"),
            ),
            es_mapping={"type": "integer"},
            search_filter=RangeFilter(
                min_date.year,
                max_date.year,
                description=("Accept only book reviews written in this range."),
            ),
            hidden=True,
        ),
        FieldDefinition(
            name="id",
            display_name="ID",
            description="ID of the review.",
            extractor=CSV("id"),
            es_mapping={"type": "keyword"},
            csv_core=True,
        ),
        FieldDefinition(
            name="book_title",
            display_name="Book title",
            description="The title of the book reviews were made for. Encompasses all editions.",
            extractor=Metadata("book_title"),
            es_mapping={"type": "keyword"},
            search_filter=MultipleChoiceFilter(
                description="Accept only reviews made for these titles.",
                option_count=154,
            ),
            csv_core=True,
        ),
        FieldDefinition(
            name="original_language",
            display_name="Original language",
            description="The original language the book reviews were made for was written in.",
            extractor=Metadata("original_language"),
            es_mapping={"type": "keyword"},
            search_filter=MultipleChoiceFilter(
                description="Accept only reviews made for titles originally in this language(s).",
                option_count=8,
            ),
            csv_core=True,
        ),
        FieldDefinition(
            name="edition_id",
            display_name="Edition ID",
            description="ID of the edition the review was made for.",
            extractor=CSV("edition_id"),
            es_mapping={"type": "keyword"},
        ),
        FieldDefinition(
            name="edition_language",
            display_name="Edition language",
            description="The language that the edition that the review is for was written in",
            extractor=CSV("edition_language"),
            es_mapping={"type": "keyword"},
            search_filter=MultipleChoiceFilter(
                description="Accept only editions written in these languages.",
                option_count=8,
            ),
            results_overview=True,
            csv_core=True,
            visualizations=["resultscount", "termfrequency"],
        ),
        FieldDefinition(
            name="book_genre",
            display_name="Genre",
            description="The genre of the reviewed book",
            extractor=Metadata("book_genre"),
            es_mapping={"type": "keyword"},
            search_filter=MultipleChoiceFilter(
                description="Accept only reviews of books in this genre", option_count=8
            ),
            visualizations=["resultscount", "termfrequency"],
        ),
        FieldDefinition(
            name="age_category",
            display_name="Age category",
            description="The age category of the target audience of the reviewed book",
            extractor=Metadata("age_category"),
            es_mapping={"type": "keyword"},
            search_filter=MultipleChoiceFilter(
                description="Accept only reviews of books written for this age category",
                option_count=3,
            ),
            visualizations=["resultscount", "termfrequency"],
        ),
        FieldDefinition(
            name="url",
            display_name="Source URL",
            display_type="url",
            description="Link to the the review on Goodreads",
            extractor=CSV("url"),
            es_mapping={"type": "keyword"},
        ),
        FieldDefinition(
            name="text",
            display_name="Text",
            description="Fulltext of the review.",
            extractor=CSV("text"),
            es_mapping=main_content_mapping(),
            display_type="text_content",
            csv_core=True,
            results_overview=True,
            searchable=True,
            visualizations=["wordcloud"],
        ),
        FieldDefinition(
            name="language",
            display_name="Review language",
            description="The language of the review.",
            extractor=CSV("language"),
            es_mapping={"type": "keyword"},
            search_filter=MultipleChoiceFilter(
                description="Accept only reviews written in these languages.",
                option_count=50,
            ),
            results_overview=True,
            csv_core=True,
            visualizations=["resultscount", "termfrequency"],
        ),
        FieldDefinition(
            name="date",
            display_name="Date",
            description="Date the review was written.",
            extractor=CSV(
                "date",
                transform=lambda x: datetime.strptime(x, "%b %d, %Y").strftime(
                    "%Y-%m-%d"
                ),
            ),
            es_mapping={"type": "date", "format": "yyyy-MM-dd"},
        ),
        FieldDefinition(
            name="rating_text",
            display_name="Goodreads rating",
            description="Rating in the Goodreads style, e.g. 'really liked it'.",
            extractor=CSV("rating"),
            es_mapping={"type": "keyword"},
        ),
        FieldDefinition(
            name="rating_no",
            display_name="Rating",
            description="Rating as a number.",
            extractor=CSV("rating_no"),
            es_mapping={"type": "keyword"},
            search_filter=MultipleChoiceFilter(
                description="Accept only reviews with these ratings.", option_count=6
            ),
            results_overview=True,
            visualizations=["resultscount", "termfrequency"],
            visualization_sort="key",
        ),
        FieldDefinition(
            name="word_count",
            display_name="Word count",
            description="Number of words (whitespace-delimited) in the review.",
            extractor=CSV("text", transform=lambda x: len(x.split(" "))),
            es_mapping={"type": "integer"},
            search_filter=RangeFilter(
                1,
                4225,
                description=("Accept only book reviews with word count in this range."),
            ),
        ),
        FieldDefinition(
            name="edition_publisher",
            display_name="Edition publisher",
            description="Publisher of the edition the review was written for",
            extractor=CSV(
                "edition_publisher",
            ),
            es_mapping={"type": "keyword"},
        ),
        FieldDefinition(
            name="edition_publishing_year",
            display_name="Edition publishing year",
            description="Year the edition the review was written for was published.",
            extractor=CSV(
                "edition_publishing_year",
            ),
            es_mapping={"type": "keyword"},
        ),
    ]

    def update_script(self):
        ''' use this script to add genre and metadata data to an existing corpus,
        without this information.
        '''
        metafile = op.join(self.data_directory, "Reviews_metadata.xlsx")
        wb = openpyxl.load_workbook(filename=metafile)
        sheet = wb['Sheet1']
        for index, row in enumerate(sheet.values):
            if index==0:
                continue
            title = row[0]
            book_genre = row[2]
            age_category = row[3]
            title_cleaned = re.sub('[^\w .-]', '', title)
            update_body = {
                "script": {
                    "source": "ctx._source['book_genre']='{}'; ctx._source['age_category']='{}'".format(book_genre, age_category),
                    "lang": "painless"
                },
                "query": {
                   "bool": {
                        "must_not": {
                            "exists": {
                                "field": "book_genre"
                            }
                        },
                        "filter": {
                            "term": {
                                "book_title": title_cleaned
                            }
                        }
                   }
                }
            }
            yield update_body
