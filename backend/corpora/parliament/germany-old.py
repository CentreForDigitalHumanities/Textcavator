from datetime import datetime

from corpora.parliament.parliament import Parliament
from ianalyzer_readers.extract import Constant, CSV
from addcorpus.python_corpora.corpus import CSVCorpusDefinition
import corpora.parliament.utils.field_defaults as field_defaults


def standardize_bool(date_is_estimate):
    return date_is_estimate.lower()

class ParliamentGermanyOld(Parliament, CSVCorpusDefinition):
    title = 'People & Parliament (Germany Reichstag - 1867-1942)'
    description = "Speeches from the Reichstag"
    min_date = datetime(year=1867, month=1, day=1)
    max_date = datetime(year=1942, month=12, day=31)
    es_index = 'parliament-germany-old'

    image = 'germany-old.jpeg'
    languages = ['de']

    description_page = 'germany-old.md'

    field_entry = 'item_order'
    required_field = 'text'

    country = field_defaults.country()
    country.extractor = Constant(
        value='Germany'
    )

    book_id = field_defaults.book_id()
    book_id.extractor = CSV('book_id')

    book_label = field_defaults.book_label()
    book_label.extractor = CSV('book_label')

    era = field_defaults.era(include_aggregations= False)
    era.extractor = CSV('parliament')

    date = field_defaults.date()
    date.extractor = CSV('date')
    date.search_filter.lower = min_date
    date.search_filter.upper = max_date

    date_is_estimate = field_defaults.date_is_estimate()
    date_is_estimate.extractor = CSV(
        'date_is_estimate',
        transform=standardize_bool
    )

    page = field_defaults.page()
    page.extractor = CSV('page_number')

    speech = field_defaults.speech(language='de')
    speech.extractor = CSV(
        'text',
        multiple=True,
        transform=lambda x : ' '.join(x)
    )

    url = field_defaults.url()
    url.extractor = CSV('img_url')

    speech_id = field_defaults.speech_id()
    speech_id.extractor = CSV('item_order')

    def __init__(self):
        self.fields = [
            self.country,
            self.book_id, self.book_label,
            self.era,
            self.date, self.date_is_estimate,
            self.page,
            self.speech, self.speech_id,
            self.url,
        ]
