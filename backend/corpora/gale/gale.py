import re
from datetime import datetime
import os.path
import PIL
from tqdm import tqdm

from ianalyzer_readers.xml_tag import Tag, SiblingTag, ParentTag
from ianalyzer_readers import extract

from addcorpus.python_corpora import filters
from addcorpus.python_corpora.corpus import XLSXCorpusDefinition, XMLCorpusDefinition, FieldDefinition
from addcorpus.es_mappings import keyword_mapping, main_content_mapping
from addcorpus.es_settings import es_settings
from api.utils import find_media_file
from media.media_url import media_url


def when_not_empty(func):
    def delegate(val):
        if val is None:
            return None
        return func(val)
    return delegate

def fix_path_sep(path):
    """Replaces backward slashes with the current platforms preferred path separator.
    Removes path spearator if present at the end of the path"""
    return path.replace('\\', os.path.sep).lstrip(os.path.sep).strip()


def clean_date(issue_date):
    if issue_date.startswith('[') and issue_date.endswith(']'):
        issue_date = issue_date[1:-1]
    if issue_date == 'Date Unknown':
        return None
    if '-' in issue_date:
        # issue date is a range
        start, end = issue_date.split('-')
        # remove ordinal suffix from day
        split = start.split()
        for sfx in ['st', 'nd', 'rd', 'th']:
            split[1] = split[1].removesuffix(sfx)
        start = ' '.join(split)
        if len(start.split()) == 3:
            # start and end date are not the same year
            return datetime.strptime(start, '%B %d %Y').strftime('%Y-%m-%d')
        # paste year from and date onto start date
        return datetime.strptime(start + ', ' + end.split(' ')[-1], '%B %d, %Y').strftime('%Y-%m-%d')
    try:
        return datetime.strptime(issue_date, '%B %d, %Y').strftime('%Y-%m-%d')
    except:
        return datetime.strptime(issue_date, '%B %d,%Y').strftime('%Y-%m-%d')


class GaleMetadata(XLSXCorpusDefinition):
    """Helper corpus for extracting metadata"""

    def __init__(self, data_directory, filename, sheet):
        self.data_directory = data_directory
        self.filename = filename
        self.sheet = sheet

    def sources(self, start=None, end=None):
        xlsx_path = os.path.join(self.data_directory, self.filename)
        yield xlsx_path, {}


    required_field = 'IssueDate'
    fields = [
        FieldDefinition(
            name='title',
            extractor=extract.CSV('PublicationTitle')
        ),
        FieldDefinition(
            name='date',
            extractor=extract.CSV(
                'IssueDate',
                transform=when_not_empty(clean_date)
            )
        ),
        FieldDefinition(
            name='image_path',
            extractor=extract.CSV(
                'ImageLocation',
                transform=when_not_empty(fix_path_sep)
            )
        ),
        FieldDefinition(
            name='data_location',
            extractor=extract.CSV(
                'DataLocation',
                transform=when_not_empty(fix_path_sep)
            )
        ),
        FieldDefinition(
            name='filename',
            extractor=extract.CSV('Filename')
        ),
        FieldDefinition(
            name='issue_id',
            extractor=extract.CSV(
                'Filename',
                transform=when_not_empty(lambda filename: filename.split("_")[0])
            )
        ),


    ]


class GaleCorpus(XMLCorpusDefinition):
    @property
    def es_settings(self):
        return es_settings(self.languages[:1])

    tag_toplevel = Tag('articles')
    tag_entry = Tag('artInfo')
    external_file_tag_toplevel = Tag('issue')

    language = 'en'
    scan_image_type = 'image/png'

    metadata_corpus = GaleMetadata

    def sources(self, start, end):
        filename, sheet = self.metafile
        metadata_corpus = self.metadata_corpus(self.data_directory, filename, sheet)
        all_metadata = {row['issue_id']: row for row in metadata_corpus.documents()}

        for issue_id in tqdm(list(all_metadata.keys())):
            metadata = all_metadata.pop(issue_id)
            external_file = os.path.join(self.data_directory, metadata['data_location'], metadata['filename'])
            xml_file = os.path.join(self.data_directory, metadata['data_location'], issue_id + '_Text.xml')
            if not os.path.isfile(xml_file):
                print("File {} not found".format(xml_file))
                continue

            metadata['external_file'] = external_file
            yield xml_file, metadata

    def process_scan(self, src):
        dst = src
        base, ext = os.path.splitext(src)
        if ext.lower() == '.tif':
            dst = base + '.png'
            if not os.path.isfile(dst):
                PIL.Image.open(src).save(dst)
        return dst

    @property
    def date(cls):
        return FieldDefinition(
            name="date",
            display_name="Publication Date",
            description="Publication date",
            es_mapping={"type": "date", "format": "yyyy-MM-dd"},
            histogram=True,
            search_filter=filters.DateFilter(
                cls.min_date,
                cls.max_date,
                description=(
                    "Accept only articles with publication date in this range."
                ),
            ),
            extractor=extract.Metadata("date"),
            csv_core=True,
            visualizations=["resultscount", "termfrequency"],
            results_overview=True
        )
    id = FieldDefinition(
        name="id",
        display_name="ID",
        description="Unique identifier of the entry.",
        es_mapping=keyword_mapping(),
        extractor=extract.XML(attribute="id"),
    )
    issue = FieldDefinition(
        name="issue",
        display_name="Issue number",
        description="Source issue number.",
        es_mapping=keyword_mapping(),
        results_overview=False,
        extractor=extract.Metadata("issue_id"),
        csv_core=False,
    )
    periodical = FieldDefinition(
        name="periodical",
        display_name="Periodical name",
        results_overview=True,
        es_mapping={"type": "keyword"},
        description="Periodical name.",
        search_filter=filters.MultipleChoiceFilter(
            description="Search only within these periodicals.", option_count=90
        ),
        extractor=extract.Metadata("title"),
        csv_core=True,
        visualizations=["resultscount", "termfrequency"],
    )

    @property
    def content(cls):
        return FieldDefinition(
            name="content",
            display_name="Content",
            display_type="text_content",
            description="Text content.",
            es_mapping=main_content_mapping(True, True, True, cls.language),
            results_overview=True,
            extractor=extract.XML(Tag("ocrText"), flatten=True),
            search_field_core=True,
            visualizations=["wordcloud", "ngram"],
            language=cls.language,
        )
    ocr = FieldDefinition(
        name="ocr",
        display_name="OCR confidence",
        description="OCR confidence level.",
        es_mapping={"type": "float"},
        search_filter=filters.RangeFilter(
            0,
            100,
            description=(
                "Accept only articles for which the Opitical Character Recognition confidence "
                "indicator is in this range."
            ),
        ),
        extractor=extract.XML(
            lambda metadata: Tag("id", string=metadata["id"]),
            SiblingTag("ocr"),
            external_file=True,
        ),
        sortable=True,
    )
    title_field = FieldDefinition(
        name="title",
        display_name="Article title",
        description="Title of the article.",
        extractor=extract.XML(
            lambda metadata: Tag("id", string=metadata["id"]),
            SiblingTag("ti"),
            external_file=True,
        ),
        visualizations=["wordcloud"],
    )
    start_column = FieldDefinition(
        name="start_column",
        es_mapping={"type": "keyword"},
        display_name="Starting column",
        description="Which column the article starts in.",
        extractor=extract.XML(
            lambda metadata: Tag("id", string=metadata["id"]),
            SiblingTag("sc"),
            external_file=True,
        ),
    )
    page_count = FieldDefinition(
        name="page_count",
        display_name="Page count",
        description="How many pages the article covers.",
        es_mapping={"type": "integer"},
        extractor=extract.XML(
            lambda metadata: Tag("id", string=metadata["id"]),
            SiblingTag("pc"),
            external_file=True,
        ),
    )
    word_count = FieldDefinition(
        name="word_count",
        display_name="Word count",
        description="Number of words in the article.",
        es_mapping={"type": "integer"},
        extractor=extract.XML(
            lambda metadata: Tag("id", string=metadata["id"]),
            SiblingTag("wordCount"),
            external_file=True,
        ),
    )
    category_field = FieldDefinition(
        name="category",
        csv_core=True,
        display_name="Category",
        description="Article category.",
        es_mapping={"type": "keyword"},
        extractor=extract.XML(
            lambda metadata: Tag("id", string=metadata["id"]),
            SiblingTag("ct"),
            external_file=True,
        ),
        search_filter=filters.MultipleChoiceFilter(
            description="Accept only articles in these categories.", option_count=26
        ),
        visualizations=["resultscount", "termfrequency"],
    )

    @property
    def page_no(self):
        # note that page number is not an integer, because it can sometimes be a roman numeral
        return FieldDefinition(
            name="page_no",
            display_name="Page number",
            description="At which page the article starts.",
            es_mapping={"type": "keyword"},
            extractor=extract.XML(
                lambda metadata: Tag("id", string=metadata["id"]),
                ParentTag(2),
                Tag("pa"),
                external_file=True,
                transform=lambda pa: self.clean_page_number(pa) if pa is not None else None
            ),
        )

    image_path = FieldDefinition(
        name="image_path",
        display_name="Image path",
        es_mapping={"type": "keyword"},
        description="Path of scan.",
        extractor=extract.Metadata("image_path"),
        hidden=True,
        downloadable=False,
    )


    @property
    def fields(self):
        return [
            self.date,
            self.id,
            self.issue,
            self.periodical,
            self.content,
            self.ocr,
            self.title_field,
            self.start_column,
            self.page_count,
            self.word_count,
            self.category_field,
            self.page_no,
            self.image_path,
        ]

    document_context = {
        'context_fields': ['issue'],
        'sort_field': 'page_no',
        'sort_direction': 'asc',
        'context_display_name': 'issue'
    }

    def resolve_media_path(self, field_vals, corpus_name):
        image_directory = field_vals['image_path']
        starting_page = field_vals['id'][:-4]
        start_index = int(starting_page.split("-")[-1])
        page_count = int(field_vals['page_count'])

        image_list = []
        for page in range(page_count):
            page_no = str(start_index + page).zfill(3)
            prefix = starting_page.rsplit('-', 1)[0]
            image_name = '{}-{}.tif'.format(prefix, page_no)
            image_path = os.path.join(image_directory, image_name)

            # while we serve PNGs, converting or looking up an existing converted file is handled in self.process_scan()
            # so here we still have to look for the source TIFFs
            full_path = find_media_file(self.data_directory, image_path, 'image/tiff')
            if full_path is not None:
                image_list.append(full_path)
            else:
                continue
        return image_list

    def request_media(self, document, corpus_name):
        media = self.resolve_media_path(document['fieldValues'], corpus_name)

        # scans are processed on the fly if they're not pre-processed
        urls = [media_url(corpus_name, self.process_scan(m)) for m in media]
        return dict(media=urls)

    def clean_page_number(self, page_no):
        # remove surrounding []s from page numbers
        # if page number is a range, keep only the first page
        return re.sub(r"[\[\]]", "", page_no).split('-')[0]
