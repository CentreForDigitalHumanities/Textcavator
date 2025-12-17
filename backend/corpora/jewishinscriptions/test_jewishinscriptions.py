import os
from corpora.utils_test import corpus_from_api

here = os.path.abspath(os.path.dirname(__file__))

def test_jewish_inscriptions(settings, db, admin_client):
    settings.CORPORA = {
        'jewish-inscriptions': 'corpora.jewishinscriptions.jewishinscriptions.JewishInscriptions',
    }
    settings.JEWISH_INSCRIPTIONS_DATA = ''

    corpus = corpus_from_api(admin_client, 'jewish-inscriptions')
    assert corpus['title'] == 'Jewish Funerary Inscriptions'
