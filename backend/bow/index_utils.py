from typing import Iterable, Tuple
from typing import Optional
from addcorpus.models import Corpus, FieldDisplayTypes, Field

def content_field_name(name: str, multifield: Optional[str] = None):
    return f'{name}.{multifield}' if multifield else name

def bow_field_name(content_field_name: str):
    return content_field_name + ':bow'

def content_fields(corpus: Corpus) -> Iterable[Field]:
    return corpus.configuration.fields.filter(
        display_type=FieldDisplayTypes.TEXT_CONTENT
    ).exclude(
        name__contains=':', # exclude programmatically generated fields
    )
