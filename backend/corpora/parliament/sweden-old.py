from glob import glob
from datetime import datetime

from addcorpus.python_corpora.corpus import CSVCorpusDefinition, get_deprecated_setting
from ianalyzer_readers.extract import CSV, Constant
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
import corpora.utils.constants as constants
import corpora.utils.formatting as formatting


def format_era(era):
    eras = {
        'standsriksdagen': 'Ståndsriksdagen',
        'tvakammarriksdagen': 'Tvåkammarriksdagen'
    }

    return eras.get(era, 'MISSING: ' + era)

def format_chamber(chamber):
    chambers = {
        'forsta': 'Första kammaren',
        'andra': 'Andra kammaren',
        'adel': 'Adel',
        'präster': 'Präster',
        'borgerskap': 'Borgerskap',
        'bönder': 'Bönder'
    }

    return chambers.get(chamber, chamber)

class ParliamentSwedenOld(Parliament, CSVCorpusDefinition):
    title = 'People and Parliament (Sweden 1809-1919)'
    description = 'Speeches from the Riksdag'
    min_date = datetime(year=1809, month=1, day=1)
    max_date = datetime(year=1919, month=12, day=31)

    @property
    def data_directory(self):
        return get_deprecated_setting('PP_SWEDEN_OLD_DATA') or super().data_directory

    @property
    def es_index(self):
        return get_deprecated_setting('PP_SWEDEN_OLD_INDEX') or 'parliament-sweden-old'

    @property
    def word_model_path(self):
        return get_deprecated_setting('PP_SWEDEN_WM') or super().word_model_path

    document_context = constants.document_context(
        context_fields=['chamber', 'date_earliest', 'date_latest']
    )
    default_sort = {
        'field': 'date_latest',
        'ascending': False,
    }

    def sources(self, start, end):
        for csv_file in sorted(glob('{}/**/*.csv'.format(self.data_directory), recursive=True)):
            yield csv_file, {}


    languages = ['sv']
    description_page = 'sweden-old.md'
    image =  'sweden-old.jpg'

    book_id = field_defaults.book_id()
    book_id.extractor = CSV('book_id')

    book_label = field_defaults.book_label()
    book_label.extractor = CSV('book_label')

    country = field_defaults.country()
    country.extractor = Constant('Sweden')

    era = field_defaults.era()
    era.extractor = CSV(
        'era',
        transform = format_era
    )

    chamber = field_defaults.chamber()
    chamber.extractor = CSV(
        'chamber',
        transform = format_chamber
    )
    chamber.search_filter.option_count = 6
    chamber.description = 'Chamber (in Tvåkammarriksdagen era) or estate (in Ståndsriksdagen era) where the debate took place'

    date_earliest = field_defaults.date_earliest()
    date_earliest.extractor = CSV('date_from')
    date_earliest.search_filter.lower = min_date
    date_earliest.search_filter.upper = max_date

    date_latest = field_defaults.date_latest()
    date_latest.extractor = CSV('date_to')
    date_latest.search_filter.lower = min_date
    date_latest.search_filter.upper = max_date

    speech = field_defaults.speech(language='sv')
    speech.extractor = CSV('text')

    page = field_defaults.page()
    page.extractor = CSV('page_number')

    sequence = field_defaults.sequence()
    sequence.extractor = CSV(
        'date_order',
        transform = formatting.extract_integer_value,
    )
    sequence.description = 'Order of documents within the same date range and chamber'

    url_pdf = field_defaults.url()
    url_pdf.extractor = CSV('pdf_url')
    url_pdf.display_name = 'Source url (PDF)'
    url_pdf.description = 'URL to PDF source file of this speech'

    url_xml = field_defaults.url()
    url_xml.extractor = CSV('xml_url')
    url_xml.name = 'url_xml'
    url_xml.display_name = 'Source url (XML)'
    url_xml.description = 'URL to XML source file of this speech'

    def __init__(self):
        self.fields = [
            self.date_earliest, self.date_latest,
            self.book_id, self.book_label,
            self.country,
            self.era,
            self.chamber,
            self.speech,
            self.page,
            self.sequence,
            self.url_pdf, self.url_xml,
        ]
