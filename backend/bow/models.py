from django.db import models
from addcorpus.models import Field
from indexing.models import IndexTask


class AddBOWFieldTask(IndexTask):
    field = models.ForeignKey(
        to=Field,
        on_delete=models.CASCADE,
        help_text='Content field for which bag-of-word data is added'
    )


class PopulateBOWFieldTask(IndexTask):
    field = models.ForeignKey(
        to=Field,
        on_delete=models.CASCADE,
        help_text='Content field for which bag-of-word data is added'
    )
    threshold = models.IntegerField(
        default=0,
        help_text='Minimum frequency threshold (across the whole corpus) for tokens',
    )
