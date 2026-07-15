import os
from addcorpus.models import Corpus

here = os.path.abspath(os.path.dirname(__file__))

def test_dbnl_validation(settings, load_test_corpus):
    settings.CORPORA = {
        'dbnl': 'corpora.dbnl.dbnl.DBNL',
    }
    settings.CORPUS_SETTINGS = {
        'dbnl': {
            'data_directory': os.path.join(here, 'data'),
        }
    }

    load_test_corpus('dbnl')

    assert Corpus.objects.filter(name='dbnl').exists()
    assert Corpus.objects.get(name='dbnl').ready_to_publish()
