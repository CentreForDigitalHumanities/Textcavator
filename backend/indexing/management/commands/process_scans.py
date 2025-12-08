import logging
import elasticsearch.helpers
from es.client import elasticsearch as es_client
from es.search import get_index
from django.core.management import BaseCommand

from addcorpus.python_corpora.load_corpus import load_corpus_definition

log = logging.getLogger(__name__)

class Command(BaseCommand):
    '''Process scan media files based on ES index.
    See CorpusDefinition.process_scan()'''
    def add_arguments(self, parser):
        parser.add_argument(
            'corpus',
        )

    def handle(self, corpus, **kwargs):
        corpus_definition = load_corpus_definition(corpus)

        client = es_client(corpus)
        index = get_index(corpus)
        results = elasticsearch.helpers.scan(client, index=index)

        for hit in results:
            doc = hit['_source']
            for scan in corpus_definition.resolve_media_path(doc, corpus):
                log.info('Processing scan: %s', scan)
                corpus_definition.process_scan(scan)
