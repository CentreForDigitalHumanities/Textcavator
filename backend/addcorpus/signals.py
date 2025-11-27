from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from addcorpus.json_corpora.csv_field_info import get_csv_info

from .models import CorpusDataFile


@receiver(post_delete, sender=CorpusDataFile)
def delete_file_on_model_delete(sender, instance: CorpusDataFile, **kwargs):
    if instance.file.storage.exists(instance.file.name):
        instance.file.storage.delete(instance.file.name)


@receiver(post_save, sender=CorpusDataFile)
def save_csv_info(sender, instance: CorpusDataFile, **kwargs):
    '''Save csv info on saving or updating data file.
    Uses .update() because .save() triggers an infinite loop of saves and signal triggers.
    '''
    csv_info = get_csv_info(instance.file.path)
    CorpusDataFile.objects.filter(id=instance.id).update(
        csv_info=csv_info)
