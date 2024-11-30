from django.apps import AppConfig

class CareeraiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'careerai'

    def ready(self):
        import careerai.templatetags.careerai_filters