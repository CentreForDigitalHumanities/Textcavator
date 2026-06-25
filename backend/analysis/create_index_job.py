from typing import Optional

from es.client import server_for_corpus
from es.search import get_index
from es.models import Index
from addcorpus.models import Corpus
from indexing.models import IndexJob
from analysis.run_index_tasks import token_index_name
from analysis.models import CreateFrequencyIndexTask, PopulateFrequencyIndexTask

def create_token_index_job(
        corpus: Corpus,
        source_index: Optional[Index] = None,
):
    server = server_for_corpus(corpus)
    if not source_index:
        index_name = get_index(corpus.name)
        source_index = Index.objects.get_or_create(
            name=index_name, server=server
        )

    job = IndexJob.objects.create(corpus=corpus)
    index_name = token_index_name(source_index.name)
    index = Index.objects.get_or_create(
        name=index_name, server=server
    )

    CreateFrequencyIndexTask.objects.create(
        job=job,
        index=index,
        source_index=source_index,
        delete_existing=True
    )

    PopulateFrequencyIndexTask.objects.create(
        job=job,
        index=index,
        source_index=source_index,
    )

    return job


