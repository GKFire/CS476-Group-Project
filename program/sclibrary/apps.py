from django.apps import AppConfig


class SCLibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sclibrary'

    def __init__(self, app_name, app_module):
        super(SCLibraryConfig, self).__init__(app_name, app_module)
        self.item_factory = None

    def ready(self):
        import sclibrary.signals  # noqa: F401  (registers signal handlers)
        if self.item_factory == None:
            from .factory.ItemFactory import ItemFactory
            self.item_factory = ItemFactory()