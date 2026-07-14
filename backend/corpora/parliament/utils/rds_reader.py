from typing import Iterable, Dict

import pyreadr
import pandas

from ianalyzer_readers.readers.core import Reader


class RDSReader(Reader):
    def data_from_file(self, path) -> Iterable[Dict]:
        result = pyreadr.read_r(path)
        for value in result.values():
            data: pandas.DataFrame = value

            for _, row in data.iterrows():
                yield {
                    index: value
                    for index, value in row.items()
                }

    def iterate_data(self, data: Iterable[Dict], metadata):
        for row in data:
            yield {'rows': [row]} # this format is for compatability with the CSV extractor
