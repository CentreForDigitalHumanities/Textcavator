import os
from corpora.utils_test import corpus_from_api

here = os.path.abspath(os.path.dirname(__file__))

def test_news_us_19(settings, db, admin_client):
    settings.CORPORA = {
        'news_us_19': os.path.join(here, 'news_us_19.py')
    }
    settings.NEWS_US_19_DATA = ''

    corpus = corpus_from_api(admin_client, 'news_us_19')
    assert corpus['title'] == '19th Century US Newspapers'
