from django.apps import AppConfig


class SCLibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sclibrary'

    def ready(self):
        import sclibrary.signals  # noqa: F401  (registers signal handlers)
