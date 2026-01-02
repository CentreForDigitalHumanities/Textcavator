from datetime import datetime
import os
import re
from glob import glob

from addcorpus.python_corpora.corpus import FieldDefinition
from addcorpus.es_mappings import main_content_mapping
from corpora.parliament.clarin_parlamint.parlamint_all import ParlaMintAll, open_xml_as_soup
from corpora.parliament.clarin_parlamint.parlamint_utils.parlamint_constants import COUNTRY_CODE_TO_NAME, LANGUAGES, DATE_RANGES
from corpora.parliament.clarin_parlamint.parlamint_utils.parlamint_extract import get_orgs_metadata, get_persons_metadata, extract_named_entities, extract_speech, get_party_list

from ianalyzer_readers.extract import XML
from ianalyzer_readers.xml_tag import Tag


def speech_extractor():
    return XML(
        Tag('s'),
        multiple=True,
        extract_soup_func = extract_speech,
        transform=' '.join
    )

class _ParlaMint(ParlaMintAll):
    country_code = None
    description_page = None

    @property
    def es_index(self):
        '''
        this property expects the full parlamint corpus to be named
        'parlamint-all', and will produce 'parlamint-at' for Austria for example
        '''
        return super().es_index.replace('all', self.country_code.lower())

    @property
    def image(self):
        return f'parlamint_{self.country_code}.jpg'
    
    def __init__(self):
        super().__init__()
    

class ParlaMintAT(_ParlaMint):
    title = "Austria"
    description = 'Speeches and debates from the national and federal councils of Austria'
    country_code = 'AT'
    country_codes = ['AT']
    languages = ['de', 'en']
    min_date = datetime(year=DATE_RANGES['AT']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['AT']['max_year'], month=12, day=31)

    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintBA(_ParlaMint):
    # TODO: check if bs is a supported language for es
    title = "Bosnia"
    description = 'Speeches and debates from the Bosnian Parliament'
    country_code = 'BA'
    country_codes = ['BA']
    languages = ['bs', 'en']
    min_date = datetime(year=DATE_RANGES['BA']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['BA']['max_year'], month=12, day=31)

    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']

class ParlaMintBE(_ParlaMint):
    # TODO: needs multilingual stemming
    title = "Belgium"
    description = 'Speeches and debates from the Belgian Parliament'
    country_code = 'BE'
    country_codes = ['BE']
    languages = ['nl', 'fr', 'en']
    min_date = datetime(year=DATE_RANGES['BE']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['BE']['max_year'], month=12, day=31)

    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintBG(_ParlaMint):
    title = "Bulgaria"
    description = 'Speeches and debates from the Bulgarian Parliament'
    country_code = 'BG'
    country_codes = ['BG']
    languages = ['bg', 'en']
    min_date = datetime(year=DATE_RANGES['BG']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['BG']['max_year'], month=12, day=31)

    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']

class ParlaMintCZ(_ParlaMint):
    title = "The Czech Republic"
    description = 'Speeches and debates from the chambers of the Czech Parliament'
    country_code = 'CZ'
    country_codes = ['CZ']
    languages = ['cs', 'en']
    min_date = datetime(year=DATE_RANGES['CZ']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['CZ']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']

class ParlaMintDK(_ParlaMint):
    title = "Denmark"
    description = 'Speeches and debates from the Danish Parliament'
    country_code = 'DK'
    country_codes = ['DK']
    languages = ['da', 'en']
    min_date = datetime(year=DATE_RANGES['DK']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['DK']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']

class ParlaMintEE(_ParlaMint):
    title = "Estonia"
    description = 'Speeches and debates from the Estonian Parliament'
    country_code = 'EE'
    country_codes = ['EE']
    languages = ['et', 'en']
    min_date = datetime(year=DATE_RANGES['EE']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['EE']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']

class ParlaMintES(_ParlaMint):
    title = "Spain"
    description = 'Speeches and debates from the Spanish Parliament'
    country_code = 'ES'
    country_codes = ['ES']
    languages = ['es', 'en']
    min_date = datetime(year=DATE_RANGES['ES']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['ES']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']

class ParlaMintESCT(_ParlaMint):
    title = "Catelonia (Spain)"
    description = 'Speeches and debates from the Catelonian Parliament'
    country_code = 'ES-CT'
    country_codes = ['ES-CT']
    languages = ['ca', 'en']
    min_date = datetime(year=DATE_RANGES['ES-CT']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['ES-CT']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintESGA(_ParlaMint):
    title = "Galicia (Spain)"
    description = 'Speeches and debates from the Galician Parliament'
    country_code = 'ES-GA'
    country_codes = ['ES-GA']
    languages = ['gl', 'en']
    min_date = datetime(year=DATE_RANGES['ES-GA']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['ES-GA']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']

class ParlaMintESPV(_ParlaMint):
    title = "Basque Country (Spain)"
    description = 'Speeches and debates from the Basque Parliament'
    country_code = 'ES-PV'
    country_codes = ['ES-PV']
    languages = ['eu', 'es', 'en']
    min_date = datetime(year=DATE_RANGES['ES-PV']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['ES-PV']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintFI(_ParlaMint):
    title = "Finland"
    description = 'Speeches and debates from the Finnish Parliament'
    country_code = 'FI'
    country_codes = ['FI']
    languages = ['fi', 'en']
    min_date = datetime(year=DATE_RANGES['FI']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['FI']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
        

class ParlaMintFR(_ParlaMint):
    title = "France"
    description = 'Speeches and debates from the French Parliament'
    country_code = 'FR'
    country_codes = ['FR']
    languages = ['fr', 'en']
    min_date = datetime(year=DATE_RANGES['FR']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['FR']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintGB(_ParlaMint):
    title = "United Kingdom"
    description = 'Speeches and debates from the British houses of Parliament'
    country_code = 'GB'
    country_codes = ['GB']
    languages = ['en']
    min_date = datetime(year=DATE_RANGES['GB']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['GB']['max_year'], month=12, day=31)

    def sources(self, *args, **kwargs):
        '''
        UK-specific sources function to simply reuse the original data for the machine-translated speech field
        '''
        country_code = self.country_code
        print("STARTING COUNTRY: GB")
        country_data_directory = os.path.join(self.data_directory, "ParlaMint-{}".format(country_code), "ParlaMint-{}.TEI.ana".format(country_code))
        persons_metadata = get_persons_metadata(country_data_directory, country_code)
        all_orgs_metadata = get_orgs_metadata(country_data_directory, country_code)
        party_list = get_party_list(all_orgs_metadata)
        metadata = {
            'persons': persons_metadata,
            'organisations': all_orgs_metadata,
            'party_list': party_list,
            'country': country_code
        }
        for year in range(DATE_RANGES[country_code]['min_year'], DATE_RANGES[country_code]['max_year']):
            for xml_file in glob('{}/ParlaMint-{}/ParlaMint-{}.TEI.ana/{}/*.xml'.format(self.data_directory, country_code, country_code, year)):
                metadata['date'] = re.search(r"\d{4}-\d{2}-\d{2}", xml_file).group()
                metadata["ner"] = extract_named_entities(xml_file)
                if os.path.exists(xml_file):
                    metadata['translated_soup'] = open_xml_as_soup(xml_file)
                yield xml_file, metadata


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
    

class ParlaMintGR(_ParlaMint):
    title = "Greece"
    description = 'Speeches and debates from the Greek Parliament'
    country_code = 'GR'
    country_codes = ['GR']
    languages = ['el', 'en']
    min_date = datetime(year=DATE_RANGES['GR']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['GR']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintHR(_ParlaMint):
    title = "Croatia"
    description = 'Speeches and debates from the Croatian Parliament'
    country_code = 'HR'
    country_codes = ['HR']
    languages = ['hr', 'en']
    min_date = datetime(year=DATE_RANGES['HR']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['HR']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
    

class ParlaMintHU(_ParlaMint):
    title = "Hungary"
    description = 'Speeches and debates from the Hungarian Parliament'
    country_code = 'HU'
    country_codes = ['HU']
    languages = ['hu', 'en']
    min_date = datetime(year=DATE_RANGES['HU']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['HU']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
    

class ParlaMintIS(_ParlaMint):
    title = "Iceland"
    description = 'Speeches and debates from the Icelandic Parliament'
    country_code = 'IS'
    country_codes = ['IS']
    languages = ['is', 'en']
    min_date = datetime(year=DATE_RANGES['IS']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['IS']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=False, # no icelandic stemming for ES
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
    

class ParlaMintIT(_ParlaMint):
    title = "Italy"
    description = 'Speeches and debates from the Italian Parliament'
    country_code = 'IT'
    country_codes = ['IT']
    languages = ['it', 'en']
    min_date = datetime(year=DATE_RANGES['IT']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['IT']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
    

class ParlaMintLV(_ParlaMint):
    title = "Latvia"
    description = 'Speeches and debates from the Latvian Parliament'
    country_code = 'LV'
    country_codes = ['LV']
    languages = ['lv', 'en']
    min_date = datetime(year=DATE_RANGES['LV']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['LV']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
    

class ParlaMintNL(_ParlaMint):
    title = "The Netherlands"
    description = 'Speeches and debates from the two chambers of Dutch Parliament'
    country_code = 'NL'
    country_codes = ['NL']
    languages = ['nl', 'en']
    min_date = datetime(year=DATE_RANGES['NL']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['NL']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
    

class ParlaMintNO(_ParlaMint):
    title = "Norway"
    description = 'Speeches and debates from the Norwegian Parliament'
    country_code = 'NO'
    country_codes = ['NO']
    languages = ['no', 'en']
    min_date = datetime(year=DATE_RANGES['NO']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['NO']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
    

class ParlaMintPL(_ParlaMint):
    title = "Poland"
    description = 'Speeches and debates from the two chambers of the Polish Parliament'
    country_code = 'PL'
    country_codes = ['PL']
    languages = ['pl', 'en']
    min_date = datetime(year=DATE_RANGES['PL']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['PL']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
    

class ParlaMintPT(_ParlaMint):
    title = "Portugal"
    description = 'Speeches and debates from the two chambers of the Portuguese Parliament'
    country_code = 'PT'
    country_codes = ['PT']
    languages = ['pt', 'en']
    min_date = datetime(year=DATE_RANGES['PT']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['PT']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
    

class ParlaMintRS(_ParlaMint):
    title = "Serbia"
    description = 'Speeches and debates from the two chambers of the Serbian Parliament'
    country_code = 'RS'
    country_codes = ['RS']
    languages = ['sr', 'en']
    min_date = datetime(year=DATE_RANGES['RS']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['RS']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=False,  # no stemmer for Serbian in ES
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintRS(_ParlaMint):
    title = "Serbia"
    description = 'Speeches and debates from the two chambers of the Serbian Parliament'
    country_code = 'RS'
    country_codes = ['RS']
    languages = ['sr', 'en']
    min_date = datetime(year=DATE_RANGES['RS']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['RS']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=False,  # no stemmer for Serbian in ES
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintSE(_ParlaMint):
    title = "Sweden"
    description = 'Speeches and debates from the Swedish Parliament'
    country_code = 'SE'
    country_codes = ['SE']
    languages = ['sv', 'en']
    min_date = datetime(year=DATE_RANGES['SE']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['SE']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintSI(_ParlaMint):
    title = "Slovenia"
    description = 'Speeches and debates from the Slovenian Parliament'
    country_code = 'SI'
    country_codes = ['SI']
    languages = ['sl', 'en']
    min_date = datetime(year=DATE_RANGES['SI']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['SI']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=False,  # no stemming for Slovenian in SE
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintTR(_ParlaMint):
    title = "Türkiye"
    description = 'Speeches and debates from the Turkish Parliament'
    country_code = 'TR'
    country_codes = ['TR']
    languages = ['tr', 'en']
    min_date = datetime(year=DATE_RANGES['TR']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['TR']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=False,  # no stemming for Slovenian in SE
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']


class ParlaMintUA(_ParlaMint):
    title = "Ukraine"
    description = 'Speeches and debates from the Ukrainian Parliament'
    country_code = 'UA'
    country_codes = ['UA']
    languages = ['uk', 'en']
    min_date = datetime(year=DATE_RANGES['UA']['min_year'], month=1, day=1)
    max_date = datetime(year=DATE_RANGES['UA']['max_year'], month=12, day=31)


    def __init__(self):
        super().__init__()
        self.speech = FieldDefinition(
            name='speech',
            display_name='Speech',
            description='The transcribed speech in the original language',
            es_mapping = main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=False,  # no stemming for Ukrainian in SE
                language=self.languages[0],
            ),
            results_overview=True,
            search_field_core=True,
            display_type='text_content',
            visualizations=['wordcloud', 'ngram'],
            csv_core=True,
            language=self.languages[0],
        )
        self.speech.extractor = speech_extractor()
        self.fields = [self.speech] + [field for field in self.fields if field.name != 'speech']
