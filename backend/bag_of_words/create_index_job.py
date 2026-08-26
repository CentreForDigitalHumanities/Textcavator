from typing import Optional

from es.client import server_for_corpus
from es.search import get_index
from es.models import Index, Server
from addcorpus.models import Corpus
from indexing.models import IndexJob
from bag_of_words.index_utils import content_fields
from bag_of_words.models import AddBOWFieldTask, PopulateBOWFieldTask



def create_bow_index_job(
        corpus: Corpus,
        index: Optional[Index] = None,
):
    server = Server.objects.get(name=server_for_corpus(corpus))
    index_name = get_index(corpus.name)
    index, _ = Index.objects.get_or_create(
        name=index_name, server=server
    )

    job = IndexJob.objects.create(corpus=corpus)

    for field in content_fields(corpus):
        AddBOWFieldTask.objects.create(
            job=job,
            index=index,
            field=field
        )
        PopulateBOWFieldTask.objects.create(
            job=job,
            index=index,
            field=field,
        )

    return job


