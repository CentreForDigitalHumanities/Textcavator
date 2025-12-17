from ianalyzer_readers.extract import Metadata

from corpora.parliament.clarin_parlamint.parlamint_all import ParlaMintAll
from corpora.parliament.clarin_parlamint.parlamint_utils.parlamint_constants import COUNTRY_CODE_TO_NAME

from addcorpus.es_mappings import keyword_mapping
from addcorpus.python_corpora.corpus import FieldDefinition

_country_field = FieldDefinition(
    name='country',
    display_name='Country',
    description='Country in which the debate took place',
    es_mapping=keyword_mapping(),
    extractor = Metadata('country', transform=lambda country_code: COUNTRY_CODE_TO_NAME[country_code]),
    visualizations=["resultscount", "termfrequency"]
)
'''Adjusted version of the country field that does not use a search filter or
visualisation'''


class _ParlaMint(ParlaMintAll):
    country_code = None

    description_page = None



    @property
    def es_index(self):
        return super().es_index + '-' + self.country_code.lower()

    @property
    def image(self):
        return f'parlamint_{self.country_code}.jpg'
    
    def __init__(self):
        super().__init__()
    
    

class ParlaMintAT(_ParlaMint):
    title = "Austria"
    description = 'Mountain Germans'
    country_code = 'AT'
    country_codes = ['AT']
    languages = ['de', 'en']

    def __init__(self):
        super().__init__()