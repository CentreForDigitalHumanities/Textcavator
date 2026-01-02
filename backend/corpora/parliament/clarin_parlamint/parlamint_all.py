import os
import re
from glob import glob
from bs4 import BeautifulSoup
from datetime import datetime

from django.conf import settings

from addcorpus.python_corpora.corpus import XMLCorpusDefinition, FieldDefinition
from addcorpus.python_corpora.filters import MultipleChoiceFilter
from addcorpus.es_settings import es_settings
from addcorpus.es_mappings import keyword_mapping, main_content_mapping
from corpora.utils.constants import document_context
from corpora.parliament.parliament import Parliament
import corpora.parliament.utils.field_defaults as field_defaults
from corpora.parliament.utils.parlamint import ner_keyword_field, speech_ner


from corpora.parliament.clarin_parlamint.parlamint_utils.parlamint_constants import COUNTRY_CODES, COUNTRY_CODE_TO_NAME, DATE_RANGES
from corpora.parliament.clarin_parlamint.parlamint_utils.parlamint_extract import get_orgs_metadata, get_persons_metadata, extract_named_entities, person_attribute_extractor, extract_speech, party_attribute_extractor, current_party_id_extractor, get_party_list
from corpora.parliament.clarin_parlamint.parlamint_utils.parlamint_transform import transform_xml_filename, transform_ministerial_role, transform_parliamentary_role, transform_political_orientation, transform_speaker_constituency, transform_government

from ianalyzer_readers.extract import Backup, XML, Combined, Order, Metadata, Pass
from ianalyzer_readers.xml_tag import Tag

def open_xml_as_soup(filepath):
    with open(filepath, 'rb') as f:
        soup = BeautifulSoup(f, features="xml")
    return soup

class ParlaMintAll(XMLCorpusDefinition):
    title = "All ParlaMint Corpora (version 5.0)"
    description = "All corpora from the ParlaMint dataset, including 27 countries"
    category = "parliament"
    image = "parlamint.png"
    description_page = "parlamint_all.md"
    languages = ['en']
    data_directory = settings.PARLAMINT_ALL_DATA
    visualize = []
    
    es_index = getattr(settings, "PARLAMINT_ALL_INDEX", 'parlamint-all')
    @property
    def es_settings(self):
        return es_settings(self.languages, stopword_analysis=True, stemming_analysis=True)

    default_sort = {'field': 'date', 'ascending': False}
    
    min_date = datetime(year=1996, month=1, day=1)
    max_date = datetime(year=2022, month=12, day=31)
    
    document_context = document_context()
    tag_toplevel = Tag('TEI')
    tag_entry = Tag('u')

    country_codes = COUNTRY_CODES
    country_code = None

    def sources(self, *args, **kwargs):
        for country_code in self.country_codes:
            print("STARTING COUNTRY: ", country_code)
            country_data_directory = os.path.join(self.data_directory, "ParlaMint-{}".format(country_code), "ParlaMint-{}.TEI.ana".format(country_code))
            country_translated_data_directory = os.path.join(self.data_directory, "ParlaMint-{}".format(country_code), "ParlaMint-{}-en.TEI.ana".format(country_code))
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
                    translated_file_path = os.path.join(
                        country_translated_data_directory,
                        str(year), 
                        transform_xml_filename(xml_file, country_code)
                    ) # en-file Path
                    if os.path.exists(translated_file_path):
                        metadata['translated_soup'] = open_xml_as_soup(translated_file_path)
                    yield xml_file, metadata

    chamber = FieldDefinition(
        name='chamber',
        display_name='Chamber',
        description='In which chamber or house of parliament in which the speeches took place',
        searchable=False,
        es_mapping=keyword_mapping(),
        search_filter=MultipleChoiceFilter(
            description='Search from speeches from the selected chamber',
            option_count=5
        ),
        extractor=XML(
            Tag('teiHeader'),
            Tag('fileDesc'),
            Tag('titleStmt'),
            Tag('meeting'),
            toplevel=True,
            attribute='corresp'
        ),
        visualizations=['resultscount', 'termfrequency']
    )

    country = FieldDefinition(
        name='country',
        display_name='Country',
        description='Country in which the debate took place',
        searchable=False,
        es_mapping=keyword_mapping(),
        search_filter = MultipleChoiceFilter(
            description='Search for speeches from the selected countries',
            option_count=len(COUNTRY_CODES)
        ),
        results_overview = True,
        extractor = Metadata('country', transform=lambda country_code: COUNTRY_CODE_TO_NAME[country_code]),
        visualizations=["resultscount", "termfrequency"]
    )
    
    date = field_defaults.date(min_date=min_date, max_date=max_date)
    date.extractor = Metadata('date')

    debate_id = field_defaults.debate_id()
    debate_id.extractor = XML(
            attribute='xml:id',
            toplevel=True,
    )

    speech_id = field_defaults.speech_id()
    speech_id.extractor = XML(
        attribute='xml:id'
    )

    speech = FieldDefinition(
        name='speech',
        display_name='Speech',
        description='The transcribed speech in the original language',
        # No stemming or stopword analysis for the full set of corpora
        es_mapping = main_content_mapping(
            token_counts=True,
            stopword_analysis=False,
            stemming_analysis=False,
            language=None,
        ),
        results_overview=False,
        search_field_core=True,
        display_type='text_content',
        visualizations=['wordcloud', 'ngram'],
        csv_core=True,
        language=None,
    )
    speech.extractor = XML(
            Tag('s'),
            multiple=True,
            extract_soup_func = extract_speech,
            transform=' '.join)
    
    def lookup_translated_speech(tuple):
        element = tuple[1].find(attrs={'xml:id': tuple[0]})
        return extract_speech(element) if element else None

    speech_translated = FieldDefinition(
        name='speech_translated',
        display_name='Speech (machine-translated)',
        description='The machine-translated speech',
        # Translated field does have stemming and stopword analysis
        es_mapping = main_content_mapping(
            token_counts=True,
            stopword_analysis=True,
            stemming_analysis=True,
            language='en',
        ),
        results_overview=True,
        search_field_core=True,
        display_type='text_content',
        visualizations=['wordcloud', 'ngram'],
        csv_core=True,
        language='en'
    )
    speech_translated.extractor = Combined(
        XML(attribute='xml:id'),
        Metadata('translated_soup'),
        transform=lookup_translated_speech
    )

    speech_ner = speech_ner()

    ner_per = ner_keyword_field("person")
    ner_loc = ner_keyword_field("location")
    ner_org = ner_keyword_field("organization")
    ner_misc = ner_keyword_field("miscellaneous")

    sequence = field_defaults.sequence()
    sequence.extractor = Order(transform=lambda value: value + 1)

    speaker = field_defaults.speaker()
    speaker.extractor = person_attribute_extractor('name')

    speaker_id = field_defaults.speaker_id()
    speaker_id.extractor = person_attribute_extractor('id')

    speaker_gender = field_defaults.speaker_gender()
    speaker_gender.extractor = person_attribute_extractor('gender')

    speaker_birth_year = field_defaults.speaker_birth_year()
    speaker_birth_year.extractor = person_attribute_extractor('birth_year')

    speaker_birthplace = field_defaults.speaker_birthplace()
    speaker_birthplace.extractor = person_attribute_extractor('birthplace')

    speaker_wikimedia = FieldDefinition(
        name = 'speaker_wikimedia',
        display_name= 'Speaker Wikipedia',
        display_type='url',
        description='URL to Wikimedia page of the speaker',
        es_mapping=keyword_mapping(),
        searchable=False,
    )

    speaker_twitter = FieldDefinition(
        name = 'speaker_twitter',
        display_name= 'Speaker Twitter',
        display_type='url',
        description='URL to Twitter page of the speaker',
        es_mapping=keyword_mapping(),
        searchable=False,
    )

    government = FieldDefinition(
        name='government',
        display_name='Government',
        description='Whether speaker is part of the government',
        es_mapping=keyword_mapping(),
        searchable=False,
        search_filter = MultipleChoiceFilter(
            description='Search speeches by members of government',
            option_count=2
        ),   
        extractor = Combined(
            person_attribute_extractor('org_nodes'),
            Metadata('date'),
            Metadata('country'),
            transform=transform_government
        )
    )

    parliamentary_role = field_defaults.parliamentary_role()
    parliamentary_role.extractor = Combined(
        person_attribute_extractor('org_nodes'),
        Metadata('date'),
        Metadata('country'),
        transform=transform_parliamentary_role
    )
    ministerial_role = field_defaults.ministerial_role()
    ministerial_role.extractor = Combined(
        person_attribute_extractor('org_nodes'),
        Metadata('date'),
        Metadata('country'),
        transform=transform_ministerial_role
    )

    current_party_id = field_defaults.party_id()
    current_party_id.extractor = current_party_id_extractor()

    current_party = field_defaults.party()
    current_party.extractor = party_attribute_extractor('name')

    current_party_full = field_defaults.party_full()
    current_party_full.extractor = party_attribute_extractor('full_name')

    current_party_wiki = FieldDefinition(
        name='party_wiki_url',
        display_name='Wikimedia URL',
        display_type='url',
        description='URL to Wikimedia page of the party',
        es_mapping=keyword_mapping(),
        searchable=False,
    )
    current_party_wiki.extractor = party_attribute_extractor('wikimedia')

    current_party_political_orientation = FieldDefinition(
        name='political_orientation',
        display_name='Political Orientation',
        description="Political leaning according to the ParlaMint team",
        es_mapping=keyword_mapping(),
        searchable=False,
        search_filter = MultipleChoiceFilter(
            description='Search for speeches from selected political leanings',
        ),
    )
    current_party_political_orientation.extractor = Pass(
        party_attribute_extractor('political_orientation'),
        transform=transform_political_orientation
    )

    speaker_constituency = field_defaults.speaker_constituency()
    speaker_constituency.extractor = Combined(
        person_attribute_extractor('org_nodes'),
        Metadata('date'),
        transform=transform_speaker_constituency
    )

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        self._fields = value
    
    def __init__(self):
        self.fields = [
            self.speech_translated,
            self.speech,
            self.chamber,
            self.country,
            self.date,
            self.debate_id,
            self.speech_id,
            self.speech_ner,
            self.sequence,
            self.speaker,
            self.speaker_id,
            self.speaker_gender,
            self.speaker_birth_year,
            self.speaker_birthplace,
            self.speaker_wikimedia,
            self.speaker_twitter,
            self.government,
            self.parliamentary_role,
            #self.ministerial_role,
            self.current_party_id,
            self.current_party,
            self.current_party_full,
            self.current_party_wiki,
            self.current_party_political_orientation,
            #self.speaker_constituency,
            self.ner_per,
            self.ner_loc,
            self.ner_org,
            self.ner_misc
        ]

