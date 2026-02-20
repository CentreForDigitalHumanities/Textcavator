from typing import Optional
from elasticsearch import NotFoundError
import warnings

from addcorpus.models import Corpus, CorpusDataFile
from es.client import server_for_corpus

from es.models import Server, Index
from es.sync import fetch_index_metadata
from es.es_alias import get_current_index_names
from es.search import get_index
from indexing.models import TaskStatus, IndexJob
from indexing.run_create_task import make_es_mapping, make_es_settings
from addcorpus.json_corpora.import_json import get_path
from addcorpus.validation.indexing import CorpusNotIndexableError


class CorpusIndexHealth:
    '''
    Reports on the "health status" of a corpus index.

    This class groups various diagnostic functions. This can be used to report on the
    index status to the user or for internal troubleshooting.
    '''

    corpus: Corpus
    server: Server
    index: Optional[Index]
    latest_job: Optional[IndexJob]
    latest_data: Optional[CorpusDataFile]


    def __init__(self, corpus: Corpus):
        self.corpus = corpus
        self.server = self._server()
        self.index = self._index(self.server)
        self.latest_job = self._latest_job()
        self.latest_file = self._latest_datafile()


    def _server(self) -> Server:
        return Server.objects.get(name=server_for_corpus(self.corpus.name))


    def _index(self, server: Server) -> Optional[Index]:
        client = server.client()
        try:
            index_names = get_current_index_names(self.corpus.configuration, client)
            assert len(index_names) <= 1
            index_name = index_names[0]
        except NotFoundError: # the corpus has no index
            index_name = get_index(self.corpus.name)
        except AssertionError: # more than one index
            warnings.warn(f'Corpus matches multiple indices')
            return
        except Exception as e: # connection issues etc.
            warnings.warn(f'Cannot connect to Elasticsearch index: {e}')
            return

        index, _ = Index.objects.get_or_create(name=index_name, server=server)

        fetch_index_metadata()
        index.refresh_from_db()

        return index


    def _latest_job(self) -> Optional[IndexJob]:
        '''
        Find the latest job for this index. Returns the most recently created job.

        Note that this is not necessarily the latest job that was completed. Mostly
        informative when the corpus is indexed through the form, which does not enable
        complex job management (such as running older jobs).
        '''
        jobs = IndexJob.objects.filter(corpus=self.corpus)
        if jobs.exists():
            return jobs.latest('created')


    def _latest_datafile(self) -> CorpusDataFile:
        '''
        Find the most recent data file for this corpus. Will not return a value for
        Python corpora.
        '''
        files = CorpusDataFile.objects.filter(corpus=self.corpus)
        if files.exists():
            return files.latest('created')


    @property
    def server_active(self) -> bool:
        '''
        Whether the server can be reached.
        '''
        return self.server.can_connect()


    @property
    def index_active(self) -> Optional[bool]:
        '''
        Whether there is an active index for the corpus.

        Returns `None` if the `index` property is empty. This happens when the server
        cannot be reached.
        '''
        if self.index:
            return self.index.available


    @property
    def settings_compatible(self) -> Optional[bool]:
        '''
        Whether the index settings in Elasticsearch are compatible with the corpus
        configuration
        '''

        if self.index and self.index.available:
            generated_settings = make_es_settings(self.corpus)
            actual_settings = self.index.settings()

            return get_path(generated_settings, 'analysis') == get_path(actual_settings, 'index', 'analysis')


    @property
    def mappings_compatible(self) -> Optional[bool]:
        '''
        Whether the field mappings in Elasticsearch match the corpus configuration
        '''
        if self.index and self.index.available:
            generated_mappings = make_es_mapping(self.corpus.configuration)
            actual_mappings = self.index.mappings()
            return generated_mappings == actual_mappings

    @property
    def index_compatible(self) -> Optional[bool]:
        return self.settings_compatible and self.mappings_compatible


    @property
    def job_status(self) -> Optional[TaskStatus]:
        '''
        Status of the last IndexJob
        '''
        if self.latest_job:
            return self.latest_job.status()

    @property
    def includes_latest_data(self) -> Optional[bool]:
        '''
        Whether the last index job included the most recent data for the corpus.

        Checks whether the job was created *after* the data was uploaded. This is
        reliable in the context of the corpus form.
        '''
        if self.latest_job and self.latest_file:
            return self.latest_job.created > self.latest_file.created

    @property
    def corpus_ready_to_index(self) -> bool:
        '''
        Whether the corpus configuration passes validation for indexing
        '''
        return self.corpus.ready_to_index()

    @property
    def corpus_validation_feedback(self) -> Optional[str]:
        '''
        If the corpus does not pass validation for indexing, returns the validation error
        message.
        '''
        try:
            self.corpus.validate_ready_to_index()
        except CorpusNotIndexableError as e:
            return str(e)

