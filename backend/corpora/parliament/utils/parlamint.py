from ianalyzer_readers.extract import XML, Combined, Metadata
from bs4.element import NavigableString
from bs4.element import NavigableString, Tag as Node
from string import punctuation
from typing import Iterable

from addcorpus.es_mappings import non_indexed_text_mapping, keyword_mapping
from ianalyzer_readers.xml_tag import Tag
from addcorpus.python_corpora.filters import MultipleChoiceFilter
from addcorpus.python_corpora.corpus import FieldDefinition

"""
This file remains in place, but it is outdated. More recent parlamint logic can be found in 
backend/corpora/parliament/clarin_parlamint/parlamint_utils. This file is kept for backwards 
compatibility for the Finland corpus.
"""


def clean_value(value):
    if type(value) == str or type(value) == NavigableString:
        stripped = value.strip()
        if len(stripped):
            return stripped
    if type(value) == int or type(value) == float:
        return value


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

def extract_person_data(node):
    id = node['xml:id']
    surname = node.persName.surname.text.strip()
    forename = node.persName.forename.text.strip()
    name = ' '.join([forename, surname])
    role = node.persName.roleName.text.strip() if node.persName.roleName else None
    gender = node.sex.text.strip() if node.sex else None

    #get party id
    is_party_node = lambda node : node.name in ['affliation', 'affiliation'] and node.has_attr('ref')
    party_node = node.find(is_party_node)
    party_id = party_node['ref'] if party_node else None

    party = party_id.split('.', maxsplit=1)[1] if party_id else None
    birth_date = node.birth['when'] if node.birth else None
    birth_year = int(birth_date[:4]) if birth_date else None

    return {
        'id': id,
        'name': name,
        'role': role,
        'gender': gender,
        'party_id': party_id,
        'party': party,
        'birth_year': birth_year,
    }

def extract_people_data(soup):
    person_nodes = soup.find_all('person')
    person_data = map(extract_person_data, person_nodes)
    return {
        '#' + person['id']: person for person in person_data
    }

def extract_role_data(soup):
    role_nodes = soup.find('encodingDesc').find_all('category')

    # return dict that maps IDs to terms
    # data contains duplicate role IDs
    # go through data in reverse order
    # so earlier (more general) terms overwrite later (more specific) ones

    return {
        node['xml:id']: node.find('term').text.strip()
        for node in reversed(role_nodes)
    }

def metadata_attribute_transform_func(attribute):
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

def party_attribute_extractor(attribute):
    """Extractor that finds the speaker's party and party's
    attributes defined in extract_party_data()'"""

    return Combined(
        person_attribute_extractor('party_id'),
        Metadata('parties'),
        transform = metadata_attribute_transform_func(attribute),
    )


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
            output += token.string if token.string else ''
    # do not include the last character (always whitespace) in the output
    return output[:-1]


def format_annotated_segment(element: Node) -> str:
    """For each <seg> tag, extract the annotations indicated by <name>"""
    annotations = element.find_all("name")
    formatted_annotations = [format_annotated_text(anno) for anno in annotations]
    return "".join(formatted_annotations)


def format_annotated_text(element: Node) -> str:
    """For each <name> tag, format the annotation in Elasticsearch's annotated_text format,
    and embed it in the text extracted from adjoining <w> and <pc> tags
    """
    output = ""
    tokens = [el.extract() for el in element.find_previous_siblings(["w", "pc"])]
    output += detokenize_parlamint(reversed(tokens))
    annotated = element.find_all("w")
    formatted = " ".join([a.string for a in annotated if a.string])
    if output:
        # if there is preceding text, add whitespace prior to annotation
        output += " "
    output += f"[{formatted}]({element['type']})"
    if not element.find_next_sibling("name"):
        # after last annotation, add remaining text
        remaining_text = detokenize_parlamint(element.find_next_siblings(["w", "pc"]))
        if remaining_text and remaining_text[0] not in punctuation:
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
