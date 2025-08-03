from django.apps import AppConfig


class CrmMedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm_med'

    def ready(self):
        from crm_med import signals  # или   import crm_med.signals
