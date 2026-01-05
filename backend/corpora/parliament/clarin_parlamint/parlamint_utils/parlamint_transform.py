import os
from bs4.element import NavigableString

from corpora.parliament.clarin_parlamint.parlamint_utils.parlamint_constants import POLITICAL_ORIENTATIONS, COUNTRY_PARLIAMENTS, COUNTRY_GOVERNMENTS

def transform_xml_filename(filepath, country_extension):
    '''transforms the original-version xml file path to the machine-translated file path'''
    filename = os.path.basename(filepath)
    transformed_filename = filename.replace(f"ParlaMint-{country_extension}", f"ParlaMint-{country_extension}-en")
    return transformed_filename

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

def clean_value(value):
    if type(value) == str or type(value) == NavigableString:
        stripped = value.strip()
        if len(stripped):
            return stripped
    if type(value) == int or type(value) == float:
        return value
    return value


def transform_political_orientation(full_string):
    if full_string and '#orientation.' in full_string:
        return POLITICAL_ORIENTATIONS[full_string.split('.')[1]]
    else:
        return None

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

def transform_parliamentary_role(data):
    check_mp = lambda node, date : node['ref'] in COUNTRY_PARLIAMENTS[country] and node['role'] == 'member' and node_is_current(node, date)
    org_nodes, date, country = data
    if not date or not country or org_nodes is None:
        return None
    if any(check_mp(node, date) for node in org_nodes):
        return 'MP'
    else:
        return 'non-MP'

def transform_ministerial_role(data):
    org_nodes, date, country = data
    for node in org_nodes:
        if COUNTRY_GOVERNMENTS[country] in node['ref'] and node['role'] == 'minister' and node_is_current(node, date):
            for child_node in node.children:
                if child_node.name == 'roleName' and child_node.get('xml:lang') == 'en':
                    return child_node.text.strip()

def transform_government(data):
    '''
    Checks a person's org_nodes for membership to a government

    Data contain:
     - org_nodes: list of BS4 nodes
     - date: string of date (YYYY-MM-DD)
     - country: string of country code (e.g. 'NL')
    '''
    org_nodes, date, country = data
    if not org_nodes:
        return 'Non-government'
    for node in org_nodes:
        if node['ref'] == COUNTRY_GOVERNMENTS[country] and node_is_current(node, date):
            return 'Government'
        else:
            return 'Non-government'
            
def transform_current_party_id(data):
    '''
    looks up party affiliation for a person at a given date. 
    The input data contain:
     - id (string)
     - persons (dictionary: {id (string): person_metadata (dict)})
     - party_list [str], list of party names
     - date (string YYYY-MM-DD)

     returns:
       str: a single party name
    '''
    id, persons, party_list, date = data
    if not id or not persons or not party_list or not date:
        return 'NA'
    current_parties = []
    is_party_node = lambda node: node['ref'] in party_list
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