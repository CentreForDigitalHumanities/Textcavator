from datetime import datetime
from corpora.parliament.uk import ParliamentUK
from corpora.utils.constants import document_context


class ParliamentUKMerged(ParliamentUK):
    title = 'UK Parliament (P&P + TE)'
    description = "Speeches from the House of Lords and House of Commons"
    min_date = datetime(year=1803, month=1, day=1)
    max_date = datetime(year=2025, month=12, day=31)
    es_index = 'parliament-uk-merged'

    image = 'uk.jpeg'
    languages = ['en']
    description_page = 'uk-merged.md'
    field_entry = 'speech_id'
    document_context = document_context()

    fields = ParliamentUK.fields
