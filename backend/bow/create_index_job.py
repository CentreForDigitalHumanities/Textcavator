from typing import Optional

from es.client import server_for_corpus
from es.search import get_index
from es.models import Index, Server
from addcorpus.models import Corpus
from indexing.models import IndexJob
from bow.index_utils import bow_index_name
from bow.models import CreateBOWIndexTask, PopulateBOWIndexTask

def create_bow_index_job(
        corpus: Corpus,
        source_index: Optional[Index] = None,
):
    server = Server.objects.get(name=server_for_corpus(corpus))
    if not source_index:
        index_name = get_index(corpus.name)
        source_index, _ = Index.objects.get_or_create(
            name=index_name, server=server
        )

    job = IndexJob.objects.create(corpus=corpus)
    index_name = bow_index_name(source_index.name)
    index, _ = Index.objects.get_or_create(
        name=index_name, server=server
    )

    CreateBOWIndexTask.objects.create(
        job=job,
        index=index,
        source_index=source_index,
        delete_existing=True
    )

    PopulateBOWIndexTask.objects.create(
        job=job,
        index=index,
        source_index=source_index,
    )

    return job


