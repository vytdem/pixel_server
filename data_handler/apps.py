from django.apps import AppConfig


class DataHandlerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_handler'

    def ready(self):
        import data_handler.signals
