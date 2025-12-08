from django.apps import AppConfig


class AddcorpusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'addcorpus'

    def ready(self):
        import addcorpus.signals
