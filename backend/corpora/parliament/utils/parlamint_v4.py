from ianalyzer_readers.extract import XML, Combined, Metadata
from bs4.element import NavigableString
from glob import glob
from string import punctuation
from typing import Iterable

from bs4.element import NavigableString, Tag as Node
from bs4 import BeautifulSoup
from ianalyzer_readers.extract import Combined, Metadata, XML
from ianalyzer_readers.xml_tag import Tag

from addcorpus.es_mappings import non_indexed_text_mapping, keyword_mapping
from addcorpus.python_corpora.corpus import FieldDefinition
from addcorpus.python_corpora.filters import MultipleChoiceFilter
from corpora.parliament.clarin_parlamint.parlamint_utils.parlamint_transform import metadata_attribute_transform_func
from corpora.parliament.clarin_parlamint.parlamint_utils.parlamint_extract import person_attribute_extractor


"""
This file was created as an updated utils file for the ParlaMint dataset, version 4.0. The previous utils file
is based on version 2.0. A more recent version of logic that exists in this file can be found in
backend/corpora/parliament/clarin_parlamint/. This file is only kept for its use in People & Parliament.
"""

POLITICAL_ORIENTATIONS = {
    'L': 'Left',
    'C': 'Centre',
    'R': 'Right',
    'FL': 'Far Left',
    'FR': 'Far Right',
    'CL': 'Centre Left',
    'CR': 'Centre Right',
    'CCL': 'Centre to Centre Left',
    'CCR': 'Centre to Centre Right',
    'CLL': 'Centre Left to Left',
    'CRR': 'Centre Right to Right',
    'LLF': 'Left to Far Left',
    'RRF': 'Right to Far Right',
    'BT': 'Big Tent',
    'NP': 'Nonpartisan',
    'PP': 'Pirate Party',
    'SI': 'Single Issue',
    'SY': 'Syncretic',
    'NA': ''
}

def clean_value(value):
    if type(value) == str or type(value) == NavigableString:
        stripped = value.strip()
        if len(stripped):
            return stripped
    if type(value) == int or type(value) == float:
        return value
    return value

def extract_org_data(node):
    id = node['xml:id']

    full_name_node = node.find('orgName', full='yes')
    full_name = full_name_node.text if full_name_node else None

    abbreviation_node = node.find('orgName', full='abb')
    name = abbreviation_node.text if abbreviation_node else full_name or id

    wikimedia_uri_node = node.find('idno', type='URI', subtype='wikimedia')
    wikimedia_uri = wikimedia_uri_node.text if wikimedia_uri_node else None

    political_orientation_node = node.find('state', type='politicalOrientation')
    political_orientation = political_orientation_node.find('state')['ana'] if political_orientation_node else None

    return {
        'name': name,
        'full_name': full_name,
        'org_role': node['role'],
        'id': id,
        'wikimedia': wikimedia_uri,
        'political_orientation': political_orientation
    }


def extract_soup(filename: str) -> Node:
    with open(filename, 'rb') as f:
        soup = BeautifulSoup(f.read(), "xml")
    return soup


def load_people_data(data_directory: str) -> Node:
    person_file = glob(f'{data_directory}/*-listPerson.xml')[0]
    return extract_soup(person_file)


def load_party_data(data_directory: str) -> Node:
    party_file = glob(f'{data_directory}/*-listOrg.xml')[0]
    return extract_soup(party_file)


def extract_all_org_data(soup):
    orgs_list = soup.find('listOrg')
    org_data = map(extract_org_data, orgs_list.find_all('org'))
    make_id = lambda name: '#' + name
    org_dict = {}
    for org in org_data:
        org_dict[make_id(org['id'])] = org
    return org_dict

def extract_person_data(node):
    id = '#' + node['xml:id']
    surname = node.persName.surname.text.strip()
    forename = node.persName.forename.text.strip()
    name = ' '.join([forename, surname])
    role = node.persName.roleName.text.strip() if node.persName.roleName else None #too simple, needs to be able to have different values and be gotten from the org_node
    gender = node.sex['value'].strip() if node.sex else None

    #get org id
    is_org_node = lambda node: node.name in ['affliation', 'affiliation'] and node.has_attr('ref')
    org_nodes = node.find_all(is_org_node)
    org_ids = [org_node['ref'] if org_node else None for org_node in org_nodes]
    birth_date = node.birth['when'] if node.birth else None
    birth_year = int(birth_date[:4]) if birth_date else None
    birthplace = node.birth.placeName.text.strip() if node.birth and node.birth.placeName else None

    wikimedia_uri_node = node.find('idno', type='URI', subtype='wikimedia')
    wikimedia_uri = wikimedia_uri_node.text if wikimedia_uri_node else None

    twitter_uri_node = node.find('idno', type='URI', subtype='twitter')
    twitter_uri = twitter_uri_node.text if twitter_uri_node else None

    return {
        'id': id,
        'name': name,
        'role': role,
        'gender': gender,
        'org_ids': org_ids,
        'org_nodes': org_nodes,  # unsure about this still: might be a bit of a memory leak to store the nodes in the metadata
        'birth_year': birth_year,
        'birthplace': birthplace,
        'wikimedia': wikimedia_uri,
        'twitter': twitter_uri,
    }

def extract_people_data(soup):
    person_nodes = soup.find_all('person')
    person_data = map(extract_person_data, person_nodes)
    return {
       person['id']: person for person in person_data
    }

def extract_role_data(soup):
    role_nodes = soup.find('encodingDesc').find_all('category')
    # return dict that maps IDs to terms data contains duplicate role IDs
    # go through data in reverse order so earlier (more general) terms 
    # overwrite later (more specific) ones
    return {
        node['xml:id']: node.find('term').text.strip()
        for node in reversed(role_nodes)
    }

def metadata_attribute_transform_func(attribute):
    """
    Creates a transformation function that extracts and cleans a specific 
    attribute from a collection.
    """
    def get_attribute(which, collection):
        if which and collection and which in collection:
            value = collection[which][attribute]
            return clean_value(value)

    return lambda values: get_attribute(*values)

def person_attribute_extractor(attribute, id_attribute = 'who'):
    """Extractor that finds the speaker ID and returns one of the person's
    attributes defined in extract_person_data()"""
    return Combined(
        XML(attribute=id_attribute),
        Metadata('persons'),
        transform = metadata_attribute_transform_func(attribute),
    )

def current_party_id_extractor():
    """Extractor that finds the current party, given a date
    if no date is given, it return the last party in the node"""
    return Combined(
        person_attribute_extractor('id'),
        Metadata('persons'),
        Metadata('date'),
        transform=transform_current_party_id
    )

def organisation_attribute_extractor(attribute):
    """Extractor that finds the speaker's party and party's
    attributes defined in extract_party_data()"""
    return Combined(
        current_party_id_extractor(),
        Metadata('organisations'),
        transform = metadata_attribute_transform_func(attribute),
    )

def node_is_current(node, date):
    """Checks if the node is current at the given date
    i.e. if the date is between the from and to dates of the node"""
    if node and date:
        start_date = node.get('from', None)
        end_date = node.get('to', None)
        if (start_date and end_date and start_date <= date <= end_date) or \
        (start_date and start_date <= date) or \
        (end_date and end_date >= date):
            return True
        else:
            return False
    else:
        return False

def transform_current_party_id(data):
    id, persons, date = data
    current_parties = []
    is_party_node = lambda node: 'party' in node['ref']
    party_nodes = [node for node in persons[id]['org_nodes'] if node and is_party_node(node)]
    if len(party_nodes) == 0:
        return 'NA'

    for node in party_nodes:
        if node_is_current(node, date):
            current_parties.append(node['ref'])

    if len(current_parties) == 1:
        return current_parties[0]
    elif len(current_parties) == 0:
        return party_nodes[-1].get('ref', 'NA')
    else:
        return current_parties[-1] #return the last org in the list since that is usually the most recent one.


def ner_keyword_field(entity: str):
    return FieldDefinition(
        name=f"{entity}:ner-kw",
        display_name=f"Named Entity: {entity.capitalize()}",
        searchable=False,
        es_mapping=keyword_mapping(enable_full_text_search=False),
        search_filter=MultipleChoiceFilter(
            description=f"Select only speeches which contain this {entity} entity",
            option_count=100,
        ),
        extractor=Combined(
            XML(attribute="xml:id"),
            Metadata("ner"),
            transform=lambda x: get_entity_list(x, entity),
        ),
    )


def detokenize_parlamint(tokens: Iterable[str]) -> str:
    """Detokenize the content of `w` and `pc` tags in the ParlaMint XML
    The `join="right"` attribute indicates that there should not be whitespace after the word
    """
    output = ""
    for token in tokens:
        if token.get("join") != "right":
            output += f"{token.string} "
        else:
            output += token.string
    # do not include the last character (always whitespace) in the output
    return output[:-1]


def format_annotated_segment(element: Node) -> str:
    """For each <seg> tag, extract the annotations indicated by <name>"""
    annotations = element.find_all("name")
    formatted_annotations = [format_annotated_text(anno) for anno in annotations]
    return "".join(formatted_annotations)


def format_annotated_text(element: Node) -> str:
    """For each <name> tag, format the annotation,
    and embed it in the text extracted from adjoining <w> and <pc> tags
    """
    output = ""
    tokens = [el.extract() for el in element.find_previous_siblings(["w", "pc"])]
    output += detokenize_parlamint(reversed(tokens))
    annotated = element.find_all("w")
    formatted = " ".join([a.string for a in annotated])
    if output:
        # if there is preceding text, add whitespace prior to annotation
        output += " "
    output += f"[{formatted}]({element['type']})"
    if not element.find_next_sibling("name"):
        # after last annotation, add remaining text
        remaining_text = detokenize_parlamint(element.find_next_siblings(["w", "pc"]))
        if remaining_text[0] not in punctuation:
            # remaining text does not start with punctuation: add whitespace
            output += " "
        output += remaining_text
    return output


def speech_ner():
    return FieldDefinition(
        name="speech:ner",
        hidden=True,
        es_mapping=non_indexed_text_mapping(),
        display_type="text_content",
        searchable=False,
        extractor=XML(
            Tag("seg"),
            multiple=True,
            extract_soup_func=format_annotated_segment,
            transform=lambda x: "\n".join(x),
        ),
    )


def extract_speech(segment: Node) -> str:
    text_nodes = segment.find_all(["w", "pc"])
    return detokenize_parlamint(text_nodes)


def get_entity_shorthand(entity: str):
    if entity == "location":
        return "LOC"
    elif entity == "miscellaneous":
        return "MISC"
    elif entity == "organization":
        return "ORG"
    else:
        return "PER"


def get_entity_list(extracted_data: tuple[str, dict], entity: str) -> list[str]:
    '''collect all named entities for the processed speech and this category

    Parameters:
        extracted_data: tuple of the speech id and the metadata dictionary
        entity: string of the entity class (location /misc / organization / person)

    '''
    speech_id, metadata = extracted_data
    shorthand = get_entity_shorthand(entity)
    return list(set(metadata.get(speech_id).get(shorthand)))


def extract_named_entities(xml_file: str) -> dict:
    '''Extract the named entities from the xml file, and save them, ordered by speech id,
    in a dictionary, which will be used to populate the NER keyword fields'''
    with open(xml_file) as f:
        soup = BeautifulSoup(f, 'xml')
    speeches = soup.find_all("u")
    output = dict()
    for speech in speeches:
        annotations_dict = {"LOC": list(), "MISC": list(), "ORG": list(), "PER": list()}
        annotations = speech.find_all("name")
        for annotation in annotations:
            annotated = " ".join([word.string for word in annotation.find_all("w")])
            annotations_dict[annotation["type"]].append(annotated)
        output[speech["xml:id"]] = annotations_dict
    return output

def extract_party_data(node):
    id = node['xml:id']

    full_name_node = node.find('orgName', full='yes')
    full_name = full_name_node.text if full_name_node else None

    abbreviation_node = node.find('orgName', full='init')
    name = abbreviation_node.text if abbreviation_node else full_name or id

    return {
        'name': name,
        'full_name': full_name,
        'role': node['role'],
        'id': id
    }

def extract_all_party_data(soup):
    parties_list = soup.find('listOrg')
    party_data = map(extract_party_data, parties_list.find_all('org'))
    make_id = lambda name: '#party.' + name if not name.startswith('party.') else '#' + name

    return {
        make_id(party['id']): party for party in party_data
    }