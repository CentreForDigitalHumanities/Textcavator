from addcorpus.python_corpora.corpus import FieldDefinition
from textcavator_readers.extract import Constant

from corpora.utils import exclude_fields

def test_exclude_fields():
    fields = [
        FieldDefinition(
            name='test1',
            extractor=Constant('some value')
        ),
        FieldDefinition(
            name='test2'
        )
    ]
    new_fields = exclude_fields.exclude_fields_without_extractor(fields)
    assert len(new_fields) == 1
