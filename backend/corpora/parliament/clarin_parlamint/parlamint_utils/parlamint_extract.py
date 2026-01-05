import os
from bs4 import BeautifulSoup

from ianalyzer_readers.extract import XML, Constant, Combined, Order, Metadata, Pass
from corpora.parliament.clarin_parlamint.parlamint_utils.parlamint_transform import metadata_attribute_transform_func, transform_current_party_id

def extract_person_data(node):
    id = '#' + node['xml:id']
    surname = node.persName.surname.text.strip() if node.persName.surname else ''
    forename = node.persName.forename.text.strip()if node.persName.forename else ''
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
        'org_nodes': org_nodes,  # unsure about this still: might be a bit much to store the nodes in the metadata
        'birth_year': birth_year,
        'birthplace': birthplace,
        'wikimedia': wikimedia_uri,
        'twitter': twitter_uri,
    }


def extract_people_data(soup):
    '''
    Takes a soup and searches it for person nodes and adds all metadata
    to a dictionary.

    Returns: a dictionary with a metadata dict for each person ID.
    '''
    person_nodes = soup.find_all('person')
    person_data = map(extract_person_data, person_nodes)
    return {
       person['id']: person for person in person_data
    }


def get_persons_metadata(directory, country_code):
    with open(os.path.join(directory, 'ParlaMint-{}-listPerson.xml'.format(country_code)), 'rb') as f:
        soup = BeautifulSoup(f.read(), 'xml')
    return extract_people_data(soup)


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


def extract_all_org_data(soup):
    orgs_list = soup.find('listOrg')
    org_data = map(extract_org_data, orgs_list.find_all('org'))
    make_id = lambda name: '#' + name
    org_dict = {}
    for org in org_data:
        org_dict[make_id(org['id'])] = org
    return org_dict


def get_orgs_metadata(directory, country_code):
    with open(os.path.join(directory, 'ParlaMint-{}-listOrg.xml'.format(country_code)), 'rb') as f:
        soup = BeautifulSoup(f.read(), 'xml')
    return extract_all_org_data(soup)

def get_party_list(org_metadata: dict) -> list:
    '''runs through organisational metadata to find the political parties'''
    party_list = []
    for org in org_metadata.keys():
        if 'org_role' in org_metadata[org] and org_metadata[org]['org_role'] in ['parliamentaryGroup', 'politicalParty']:
            party_list.append(org)
    return party_list


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
            annotated = " ".join([word.string for word in annotation.find_all("w") if word.string])
            annotations_dict[annotation["type"]].append(annotated)
        output[speech["xml:id"]] = annotations_dict
    return output


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
        Metadata('party_list'),
        Metadata('date'),
        transform=transform_current_party_id
    )

def party_attribute_extractor(attribute):
    """Extractor that finds the speaker's party and party's
    attributes defined in extract_party_data()"""
    return Combined(
        current_party_id_extractor(),
        Metadata('organisations'),
        transform = metadata_attribute_transform_func(attribute),
    )

def extract_speech(element):
    """
    Extracts all string values from the given BeautifulSoup element (in this case 
    one sentence from a speech) and joins them into a single string.
    Preserves spaces between words but not between words and punctuation.

    Args:
        element (bs4.PageElement): The BeautifulSoup element to process.

    Returns:
        str: A single string containing a sentence.
    """
    sentence = []
    for string in element.stripped_strings:
        # Dealing with punctuation
        if string in [',', '.', '!', '?', ';', ':', ')', ']', '}']:
            if sentence and sentence[-1].endswith(' '):
                sentence[-1] = sentence[-1][:-1] + string + ' '
            else:
                sentence.append(string + ' ')
        elif string in ["-"]:  # hyphenated-words
            if sentence and sentence[-1].endswith(' '):
                sentence[-1] = sentence[-1][:-1] + string
            else:
                sentence.append(string)
        elif string.startswith("'"):  # contractions are stored as "'s", "'m"
            if sentence and sentence[-1].endswith(' '):
                sentence[-1] = sentence[-1][:-1] + string + ' '
            else:
                sentence.append(string + ' ')
        elif string in ['(', '[', '{']:
            sentence.append(string)
        else:
            sentence.append(string + ' ')
    if len(sentence) > 1:
        sentence[-1] = sentence[-1][:-1] if sentence[-1].endswith(' ') else sentence[-1] #trailspaces
    return ''.join(sentence)