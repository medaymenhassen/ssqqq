from django.apps import AppConfig


class BodyanalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bodyanalytics'

    def ready(self):
        import bodyanalytics.signals
