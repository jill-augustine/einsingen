from django.apps import AppConfig


class EinsingenApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # Full Python path to the application
    name = "einsingen_django.api"
    verbose_name = "Einsingen API"
