from django.db import models
from addcorpus.models import Field
from indexing.models import IndexTask
from bag_of_words.run_index_tasks import add_bow_field, populate_bow_field


class AddBOWFieldTask(IndexTask):
    field = models.ForeignKey(
        to=Field,
        on_delete=models.CASCADE,
        help_text='Content field for which bag-of-word data is added'
    )

    def hande(self):
        add_bow_field(self)


class PopulateBOWFieldTask(IndexTask):
    field = models.ForeignKey(
        to=Field,
        on_delete=models.CASCADE,
        help_text='Content field for which bag-of-word data is added'
    )

    def handle(self):
        populate_bow_field(self)
