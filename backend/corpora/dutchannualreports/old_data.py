import csv
import re
import os
import os.path as op
import logging
from datetime import datetime
from ianalyzer_readers.xml_tag import Tag

from django.conf import settings

from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.readers.xml import XMLReader
from ianalyzer_readers.extract import XML, Metadata, Combined
from addcorpus.python_corpora.corpus import FieldDefinition


class DutchAnnualReportsOldDataReader(XMLReader):
    """
    Reader for the 1957-2008 data for Dutch Annual reports corpus.

    There are alto XML files with extra metadata files.
    """

    min_date = datetime(year=1957, month=1, day=1)
    max_date = datetime(year=2008, month=12, day=31)

    @property
    def data_directory(self):
        return settings.DUTCHANNUALREPORTS_DATA

    tag_toplevel = Tag('alto')
    tag_entry = Tag('Page')

    # New data members
    non_xml_msg = 'Skipping non-XML file {}'
    non_match_msg = 'Skipping XML file with nonmatching name {}'

    def __init__(self):
        self.dutchannualreports_map = {}

        with open(op.join(os.path.dirname(__file__), 'dutchannualreports_mapping.csv')) as f:
            reader = csv.DictReader(f)
            self.dutchannualreports_map = {
                line['abbr'].upper(): line['name']
                for line in reader
            }


    def sources(self, start=min_date, end=max_date):
         # make the mapping dictionary from the csv file defined in config
        logger = logging.getLogger(__name__)
        for directory, _, filenames in os.walk(self.data_directory):
            rel_dir = op.relpath(directory, self.data_directory)
            _, tail = op.split(directory)
            if tail == "Financials":
                company_type = "Financial"
            elif tail == "Non-Financials":
                company_type = "Non-financial"
            for filename in filenames:
                name, extension = op.splitext(filename)
                full_path = op.join(directory, filename)
                file_path = op.join(rel_dir, filename)
                image_path = op.join(
                    rel_dir, name + '.pdf')
                if extension != '.xml':
                    logger.debug(self.non_xml_msg.format(full_path))
                    continue
                information = re.split("_", name)
                # financial folders contain multiple xmls, ignore the abby files
                if information[-1] == "abby" or len(information[-1]) > 5:
                    continue
                company = information[0]
                if re.match("[a-zA-Z]+", information[1]):
                    # second part of file name is part of company name
                    company = "_".join([company, information[1]])
                # using first four-integer string in the file name as year
                years = re.compile(r"[0-9]{4}")
                year = next((re.match(years, info).group(0) for info in information
                             if re.match(years, info)), None)
                if len(information) == 3:
                    serial = information[-1]
                    scan = "00001"
                else:
                    serial = information[-2]
                    scan = information[-1]
                # to do: what about year reports which are combined (e.g. "1969_1970" in filepath)
                # or which cover parts of two years ("br" in filepath)?
                if year and year.isnumeric() and int(year) < start.year or end.year < int(year):
                    continue
                yield full_path, {
                    'file_path': file_path,
                    'image_path': image_path,
                    'company': company,
                    'company_type': company_type,
                    'year': year,
                    'serial': serial,
                    'scan': scan,
                }

    @property
    def fields(self):
        return [
            FieldDefinition(
                name='year',
                extractor=Metadata(key='year', transform=int),
            ),
            FieldDefinition(
                name='company',
                extractor=Metadata(
                    key='company',
                    transform=lambda x: self.dutchannualreports_map[x.upper()],
                ),
            ),
            FieldDefinition(
                name='company_type',
                extractor=Metadata(key='company_type')
            ),
            FieldDefinition(
                name='page',
                extractor=XML(attribute='PHYSICAL_IMG_NR', transform=int),
            ),
            FieldDefinition(
                name='id',
                extractor=Combined(
                    Metadata(key='company'),
                    Metadata(key='year'),
                    XML(attribute='ID'),
                    transform=lambda x: '_'.join(x),
                ),
            ),
            FieldDefinition(
                name='content',
                extractor=XML(
                    Tag('String'),
                    attribute='CONTENT',
                    multiple=True,
                    transform=lambda x: ' '.join(x),
                ),
            ),
            Field(
                name='file_path',
                extractor=Metadata(key='file_path'),
            ),
            Field(
                name='image_path',
                extractor=Metadata(key='image_path'),
            )
        ]
