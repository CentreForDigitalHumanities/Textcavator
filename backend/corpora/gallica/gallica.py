from datetime import datetime
import logging
import os.path as op
from time import sleep
from typing import Union

from bs4 import BeautifulSoup
from ianalyzer_readers.xml_tag import Tag
from ianalyzer_readers.extract import Metadata, XML
import requests
from requests.exceptions import ConnectionError as RequestsConnectionError

from addcorpus.python_corpora.corpus import XMLCorpusDefinition
from addcorpus.python_corpora.corpus import FieldDefinition
from addcorpus.python_corpora.filters import DateFilter
from addcorpus.es_mappings import (
    keyword_mapping,
    date_mapping,
    main_content_mapping,
)
from addcorpus.es_settings import es_settings

logger = logging.getLogger('indexing')

def get_content(content: BeautifulSoup) -> str:
    """Return text content in the parsed HTML file from the `texteBrut` request
    This is contained in the first <p> element after the first <hr> element.
    """
    text_nodes = content.find("hr").find_next_siblings("p")
    return "".join([node.get_text() for node in text_nodes])


def get_publication_id(identifier: str) -> str:
    try:
        return identifier.split("/")[-1]
    except IndexError:
        return None


def join_issue_strings(issue_description: Union[list[str], None]) -> Union[str, None]:
    if issue_description:
        return "".join(issue_description[:2])


class Gallica(XMLCorpusDefinition):

    languages = ["fr"]
    data_url = "https://gallica.bnf.fr"
    corpus_id = ""  # each corpus on Gallica has an "ark" id
    scan_image_type = "image/jpeg"
    n_retries = 5
    data_directory = op.dirname(
        op.abspath(__file__)
    )  # make sure that all corpora have a data_directory assigned

    @property
    def es_settings(self):
        return es_settings(self.languages[:1])

    def sources(self, start: datetime, end: datetime):
        # obtain list of ark numbers
        response = requests.get(
            f"{self.data_url}/services/Issues?ark=ark:/12148/{self.corpus_id}/date"
        )
        if response.status_code == 200:
            year_soup = BeautifulSoup(response.content, "xml")
            years = [
                year.string
                for year in year_soup.find_all("year")
                if int(year.string) >= start.year and int(year.string) <= end.year
            ]
        else:
            logger.warning(f"The date request for {self.corpus_id} failed.")
            yield None
        for year in years:
            for retry in range(self.n_retries):
                sleep(retry * 10)
                try:
                    response = requests.get(
                        f"{self.data_url}/services/Issues?ark=ark:/12148/{self.corpus_id}/date&date={year}"
                    )
                    if response.status_code == 200:
                        ark_soup = BeautifulSoup(response.content, "xml")
                        ark_numbers = [
                            issue_tag["ark"] for issue_tag in ark_soup.find_all("issue")
                        ]
                        break
                except RequestsConnectionError:
                    logger.warning(
                        f"Connection error when processing year {year}, going to sleep for {retry * 10} seconds"
                    )
                    continue

            for ark in ark_numbers:
                for retry in range(self.n_retries):
                    sleep(retry * 10)
                    try:
                        source_response = requests.get(
                            f"{self.data_url}/services/OAIRecord?ark={ark}"
                        )
                        if source_response.status_code == 200:
                            break
                    except RequestsConnectionError:
                        logger.warning(
                            f"Connection error encountered in issue {ark}, going to sleep for {retry * 10} seconds"
                        )
                        continue
                for retry in range(self.n_retries):
                    sleep(retry * 10)
                    try:
                        content_response = requests.get(
                            f"{self.data_url}/ark:/12148/{ark}.texteBrut"
                        )
                        if content_response.status_code == 200:
                            parsed_content = BeautifulSoup(
                                content_response.content, "lxml-html"
                            )
                            break
                    except RequestsConnectionError:
                        logger.warning(
                            f"Connection error when fetching full text of issue {ark}, going to sleep for {retry * 10} seconds"
                        )
                        continue
                yield (
                    source_response,
                    {"content": parsed_content},
                )

    def content(self):
        return FieldDefinition(
            name="content",
            description="Content of publication",
            display_name="Content",
            display_type="text_content",
            results_overview=True,
            search_field_core=True,
            es_mapping=main_content_mapping(
                token_counts=True,
                stopword_analysis=True,
                stemming_analysis=True,
                language=self.languages[0],
            ),
            extractor=Metadata("content", transform=get_content),
            visualizations=['wordcloud', 'ngram'],
        )

    def contributor(self):
        return FieldDefinition(
            name="contributor",
            display_name="Contributors",
            description="Persons who contributed to this periodical",
            es_mapping=keyword_mapping(enable_full_text_search=True),
            extractor=XML(Tag("dc:contributor"), multiple=True),
        )

    def date(self, min_date: datetime, max_date: datetime):
        return FieldDefinition(
            name="date",
            display_name="Date",
            description="The date of the publication.",
            es_mapping=date_mapping(),
            extractor=XML(
                Tag("dc:date"),
            ),
            results_overview=True,
            search_filter=DateFilter(
                min_date, max_date, description="Search only within this time range."
            ),
            visualizations=["resultscount", "termfrequency"],
            csv_core=True,
        )

    def identifier(self):
        return FieldDefinition(
            name="id",
            display_name="Publication ID",
            description="Identifier of the publication on Gallica",
            es_mapping=keyword_mapping(),
            extractor=XML(Tag("dc:identifier"), transform=get_publication_id),
            csv_core=True,
        )

    def issue(self):
        return FieldDefinition(
            name="issue",
            description="Issue description",
            es_mapping=keyword_mapping(),
            extractor=XML(
                Tag("dc:description"), multiple=True, transform=join_issue_strings
            ),
        )

    def periodical_title(self):
        return FieldDefinition(
            name="title",
            display_name="Title",
            description="Full title of the journal",
            es_mapping=keyword_mapping(enable_full_text_search=True),
            extractor=XML(Tag("dc:title")),
        )

    def publisher(self):
        return FieldDefinition(
            name="publisher",
            display_name="Publisher",
            description="Publisher of this periodical",
            es_mapping=keyword_mapping(),
            extractor=XML(
                Tag("dc:publisher"), multiple=True, transform=lambda x: "".join(x)
            ),
        )

    def url(self):
        return FieldDefinition(
            name="url",
            display_name="Source URL",
            display_type="url",
            description="URL to scan on Gallica",
            es_mapping=keyword_mapping(),
            extractor=XML(Tag("dc:identifier")),
            searchable=False,
        )

    def request_media(self, document, corpus_name):
        """
        Return the media URLs for a given document from the Gallica website
        This method assumes that all Gallica images are stored in the same way,
        i.e. by adding "/f1.highres" to the URL.
        """
        full_image_path = document['fieldValues'].get('url') + "/f1.highres"
        image_urls = [full_image_path]
        return {'media': image_urls}

    # define fields property so it can be set in __init__
    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        self._fields = value
