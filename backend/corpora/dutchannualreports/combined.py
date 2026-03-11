# TODO: delete this and import from ianalyzer_readers
'''
Module for "meta-readers" that combine output from other readers. Currently, this is
just the `ConcatReader`.
'''

from typing import List, Type, Tuple, Dict
from ianalyzer_readers.readers.core import Reader, Source, SourceData

class ConcatReader(Reader):
    '''
    A ConcatReader returns data from multiple subreaders.

    The combined reader will iterate through each subreader in turn and concatenate the
    documents. For example, you could use this when a portion of your data is provided as
    XML files, and another portion as CSV files.

    To make a working combined reader, you need to implement `reader_classes`, which
    provides the classes of the subreaders, and `fields`. The fields do not need
    (or use) extractors. Field values are taken directly from the subreader by matching
    the name. If a subreader does not implement a field, its value will be `None`.

    Attributes:
        reader_classes: List of classes for subreaders.
    '''

    reader_classes: List[Type[Reader]]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.readers = [cls(**kwargs) for cls in self.reader_classes]


    def sources(self, **kwargs):
        for i, reader in enumerate(self.readers):
            for source in reader.sources(**kwargs):
                source_data, metadata = self._split_metadata(source)
                metadata = metadata | {'reader_index': i}
                yield source_data, metadata


    def source2dicts(self, source: Source, **kwargs):
        _, metadata = self._split_metadata(source)
        reader: Reader = self.readers[metadata['reader_index']]
        docs = reader.source2dicts(source, **kwargs)

        for doc in docs:
            yield {field.name: doc.get(field.name, None) for field in self.fields}

    def _split_metadata(self, source: Source) -> Tuple[SourceData, Dict]:
        '''Splits a source into the (unparsed) source object and metadata'''
        if isinstance(source, tuple) and len(source) == 2:
            return source
        else:
            return source, {}
