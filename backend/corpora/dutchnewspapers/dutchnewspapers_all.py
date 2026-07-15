from django.conf import settings
from datetime import datetime

from corpora.dutchnewspapers.dutchnewspapers_public import DutchNewspapersPublic

class DutchNewsPapersAll(DutchNewspapersPublic):
    '''
    The complete KB newspapers

    Note that the parent class DutchNewspapersPublic cannot be evaluated
    without being added to the corpora in django settings - hence it is not possible
    to use this corpus without including the public counterpart in your environment.
    '''

    title = "Dutch Newspapers (full)"
    description = "Full collection of Dutch newspapers digitised by the Koninklijke Bibliotheek."
    es_index = 'dutchnewspapers-all'
    max_date = datetime(year=1995, month=12, day=31)

    def update_body(self, doc=None):
        if not doc:
            return True
        url = "http://resolver.kb.nl/resolve?urn=ddd:{}:mpeg21:{}".format(*doc['_id'].split(":"))
        return {
            "doc": {
                "url" : url
            }
        }

    def update_query(self, min_date, max_date):
        return {
            "query" : {
                "range" : { "date" : {
                    "gte": min_date,
                    "lte": max_date
                }}
            }
        }
