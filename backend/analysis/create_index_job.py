from typing import Optional

from es.client import server_for_corpus
from es.search import get_index
from es.models import Index, Server
from addcorpus.models import Corpus
from indexing.models import IndexJob
from analysis.index_utils import token_index_name
from analysis.models import CreateTokenIndexTask, PopulateTokenIndexTask

def create_token_index_job(
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
    index_name = token_index_name(source_index.name)
    index, _ = Index.objects.get_or_create(
        name=index_name, server=server
    )

    CreateTokenIndexTask.objects.create(
        job=job,
        index=index,
        source_index=source_index,
        delete_existing=True
    )

    PopulateTokenIndexTask.objects.create(
        job=job,
        index=index,
        source_index=source_index,
    )

    return job


