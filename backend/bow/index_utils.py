from typing import Iterable
from typing import Optional
from addcorpus.models import Corpus, FieldDisplayTypes, Field


def bow_field_name(content_field_name: str):
    return content_field_name + ':bow'


def token_field_name(field_name: str, multifield: Optional[str] = None):
    return f'{field_name}.{multifield}' if multifield else field_name


def content_fields(corpus: Corpus) -> Iterable[Field]:
    return corpus.configuration.fields.filter(
        display_type=FieldDisplayTypes.TEXT_CONTENT
    ).exclude(
        name__contains=':', # exclude programmatically generated fields
    )
