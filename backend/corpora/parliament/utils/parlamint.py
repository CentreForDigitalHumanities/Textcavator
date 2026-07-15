from textcavator_readers.extract import XML, Combined, Metadata
from bs4.element import NavigableString

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
