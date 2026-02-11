from elasticsearch import Elasticsearch
from django.conf import settings

def elasticsearch(corpus_name):
    '''
    Create ElasticSearch instance for a corpus.

    If multiple Elasticsearch servers are configured in the project, the server is
    selected based on the CORPUS_SERVER_NAMES setting.
    '''
    server_name = server_for_corpus(corpus_name)
    config = settings.SERVERS.get(server_name)

    return client_from_config(config)

def server_for_corpus(corpus_name) -> str:
    return settings.CORPUS_SERVER_NAMES.get(corpus_name, 'default')


def client_from_config(server_config):
    '''
    Create an Elasticsearch instance from server configuration
    '''
    node = {'host': server_config['host'],
            'port': int(server_config['port']),
            'scheme': 'http'
    }
    kwargs = {
        'max_retries': 15,
        'retry_on_timeout': True,
        'request_timeout': 60
    }
    if server_config.get('certs_location') and server_config.get('api_key'):
        # settings to connect via SSL are present
        node['scheme'] = 'https'
        kwargs['ca_certs'] = server_config.get('certs_location')
        kwargs['api_key'] = (server_config.get('api_id'), server_config.get('api_key'))
    client = Elasticsearch([node], **kwargs)
    return client
