from django.db import models
from indexing.models import IndexTask, Index

class CreateBOWIndexTask(IndexTask):
    source_index = models.ForeignKey(
        to=Index,
        on_delete=models.CASCADE,
        help_text='Index containing source data'
    )
    delete_existing = models.BooleanField(
        default=False,
        help_text='Delete index if it exists already'
    )

class PopulateBOWIndexTask(IndexTask):
    source_index = models.ForeignKey(
        to=Index,
        on_delete=models.CASCADE,
        help_text='Index containing source data'
    )
    threshold = models.IntegerField(
        default=0,
        help_text='Minimum frequency threshold (across the whole corpus) for tokens',
    )
